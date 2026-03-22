import json
import os
import re
from typing import Any, Dict, Iterable, List, Tuple, Set

from DrissionPage import Chromium
from htmlprocess2 import GDTHtmlParser


class WebsiteCrawler:
    def __init__(self, start_url: str, output_dir: str = "guidelines_data"):
        print(f"[*] 正在初始化浏览器引擎...")
        self.browser = Chromium()
        self.url = start_url
        self.output_dir = output_dir

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[+] 存储目录已就绪: {self.output_dir}")

        self.parser = GDTHtmlParser()

    # -----------------------------
    # helpers: detect / traverse HTML strings in JSON
    # -----------------------------
    def _looks_like_html(self, s: str) -> bool:
        """
        尽量稳健地判断字符串是否为 HTML/HTML片段：
        - 有尖括号
        - 且包含常见标签开头（避免把类似 "a<b" 误判）
        """
        if not isinstance(s, str):
            return False
        if "<" not in s or ">" not in s:
            return False
        low = s.lower()
        return any(tag in low for tag in ("<html", "<div", "<table", "<body", "<p", "<span", "<thead", "<tbody", "<tr", "<td"))

    def _ensure_document(self, s: str) -> str:
        """
        GDTHtmlParser 对完整 HTML 文档最稳。
        如果是 fragment，则包一层最小 html/body。
        """
        low = s.lstrip().lower()
        if "<html" in low and "</html>" in low:
            return s
        return f"<!doctype html><html><head><meta charset='utf-8'></head><body>{s}</body></html>"

    def _iter_paths(self, obj: Any, path: str = "") -> Iterable[Tuple[str, Any]]:
        """
        遍历任意 dict/list，产出 (path, value)
        path 形如：profile.extra.oneRowSource 或 items[0].html
        """
        yield path, obj
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = f"{path}.{k}" if path else str(k)
                yield from self._iter_paths(v, p)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                p = f"{path}[{i}]"
                yield from self._iter_paths(v, p)

    def _is_excluded_path(self, path: str, excluded_keys: Set[str]) -> bool:
        """
        排除已处理的三个字段：只要 path 以 .<key> 结尾或包含 .<key> 都排除
        """
        for k in excluded_keys:
            # 常见：profile.extra.oneRowSource
            if path.endswith("." + k) or (("." + k + ".") in path) or path.endswith(k):
                return True
        return False

    # -----------------------------
    # newclean: main processing pipeline
    # -----------------------------
    def newclean(self, data_dict: Dict[str, Any], p_title: str, save_name: str = "cleaned.json") -> Dict[str, Any]:
        """
        主处理函数：输入原始响应 dict，输出清洗并解析后的 dict，并保存为 json。
        """
        cleaned_dict: Dict[str, Any] = {}
        excluded_html_keys = {"oneRowSource", "ietdPrintout", "sofSource"}

        # 1) question
        cleaned_dict["question"] = data_dict.get("profile", {}).get("title")
        if not cleaned_dict["question"]:
            qs = data_dict.get("profile", {}).get("sofTitle")
            cleaned_dict["question"] = ("Should " + qs) if qs else p_title

        # 2) parse the known 3 html fields into cleaned_dict
        extra = data_dict.get("profile", {}).get("extra", {}) if isinstance(data_dict, dict) else {}

        cleaned_dict["parsed_known_html"] = {}
        for k in ("oneRowSource", "ietdPrintout", "sofSource"):
            raw_html = extra.get(k)
            if isinstance(raw_html, str) and raw_html.strip():
                doc = self._ensure_document(raw_html)
                cleaned_dict["parsed_known_html"][k] = self.parser.parse(doc)
            else:
                cleaned_dict["parsed_known_html"][k] = None

        # 3) traverse whole raw dict and parse other html strings (excluding the 3)
        cleaned_dict["extra_html_parsed"] = {}

        seen_hashes: Set[str] = set()
        for path, value in self._iter_paths(data_dict):
            if not isinstance(value, str):
                continue
            if self._is_excluded_path(path, excluded_html_keys):
                continue
            if not self._looks_like_html(value):
                continue

            # 去重：同样的 HTML 内容可能出现在多个字段
            h = hash(value)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            try:
                doc = self._ensure_document(value)
                parsed = self.parser.parse(doc)
                cleaned_dict["extra_html_parsed"][path] = parsed
            except Exception as e:
                # 不中断：保存错误信息，便于定位
                cleaned_dict["extra_html_parsed"][path] = {"_error": str(e)}

        # 4) save json
        out_path = os.path.join(self.output_dir, save_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_dict, f, ensure_ascii=False, indent=2)
        print(f"[+] cleaned_dict 已保存: {out_path}")

        return cleaned_dict

    # -----------------------------
    # crawl
    # -----------------------------
    def crawl(self, xhr_target: str, timeout: int = 20, save_name: str = "cleaned.json") -> Dict[str, Any]:
        tab = self.browser.latest_tab
        tab.listen.start(targets=xhr_target, res_type="xhr")
        tab.get(self.url)
        res = tab.listen.wait(timeout=timeout)
        if not res:
            raise TimeoutError("XHR wait timeout / no response captured")

        rawdict = res.response.body
        # p_title 兜底：你也可以换成 profile id 等
        cleaned = self.newclean(rawdict, p_title="UNKNOWN_TITLE", save_name=save_name)
        return cleaned


if __name__ == "__main__":
    TARGET_URL = "https://guidelines.gradepro.org/profile/Lfz8s2r0kpE"
    XHR_TARGET = "Lfz8s2r0kpE"  # 你原来的 targets 值

    crawler = WebsiteCrawler(start_url=TARGET_URL)
    try:
        crawler.crawl(xhr_target=XHR_TARGET, timeout=20, save_name="test_cleaned3.json")
    except KeyboardInterrupt:
        print("\n[!] 用户中断操作")
    finally:
        print("\n[*] 正在安全退出...")
        crawler.browser.quit()