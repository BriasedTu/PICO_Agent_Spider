import json
import os
import re
import time
from typing import Any, Dict, Iterable, Tuple, Set, Optional, List

from DrissionPage import Chromium
from htmlprocess2 import GDTHtmlParser


class WebsiteCrawler:
    def __init__(
        self,
        start_urls: List[str],
        output_dir: str = "guidelines_data",
        raw_dir: str = "guidelines_raw",
        timeout: int = 25,
    ):
        print("[*] 正在初始化浏览器引擎...")
        self.browser = Chromium()
        self.start_urls = start_urls
        self.output_dir = output_dir
        self.raw_dir = raw_dir
        self.timeout = timeout

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.raw_dir, exist_ok=True)
        print(f"[+] 结构化输出目录: {self.output_dir}")
        print(f"[+] 原始XHR备份目录: {self.raw_dir}")

        self.parser = GDTHtmlParser()

        # 去重：同名（清洗后的 p_title）只爬一次（跨所有搜索页/搜索词）
        self.seen_titles: Set[str] = set()

    # -----------------------------
    # filename / title normalization
    # -----------------------------
    def clean_p_title(self, title: str, max_len: int = 120) -> str:
        """
        用于文件名：全部小写 + 安全字符 + 合并多下划线
        """
        if not title:
            title = "untitled"
        title = title.strip().lower()  # 你要求：所有字母小写
        # 把非字母数字替换为 _
        title = re.sub(r"[^a-z0-9]+", "_", title)
        title = re.sub(r"_+", "_", title).strip("_")
        if not title:
            title = "untitled"
        if len(title) > max_len:
            title = title[:max_len].rstrip("_")
        return title

    # -----------------------------
    # helpers: detect / traverse HTML strings in JSON
    # -----------------------------
    def _looks_like_html(self, s: str) -> bool:
        if not isinstance(s, str):
            return False
        if "<" not in s or ">" not in s:
            return False
        low = s.lower()
        return any(tag in low for tag in (
            "<html", "<div", "<table", "<body", "<p", "<span", "<thead", "<tbody", "<tr", "<td"
        ))

    def _ensure_document(self, s: str) -> str:
        low = s.lstrip().lower()
        if "<html" in low and "</html>" in low:
            return s
        return f"<!doctype html><html><head><meta charset='utf-8'></head><body>{s}</body></html>"

    def _iter_paths(self, obj: Any, path: str = "") -> Iterable[Tuple[str, Any]]:
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
        for k in excluded_keys:
            if path.endswith("." + k) or (("." + k + ".") in path) or path.endswith(k):
                return True
        return False

    # -----------------------------
    # data processing (clean + parse)
    # -----------------------------
    def newclean(self, data_dict: Dict[str, Any], p_title_for_question: str) -> Dict[str, Any]:
        """
        输入：原始XHR dict
        输出：清洗解析后的 dict（不写文件，由上层负责写）
        """
        cleaned_dict: Dict[str, Any] = {}
        excluded_html_keys = {"oneRowSource", "ietdPrintout", "sofSource"}

        # 1) question
        cleaned_dict["question"] = data_dict.get("profile", {}).get("title")
        if not cleaned_dict["question"]:
            qs = data_dict.get("profile", {}).get("sofTitle")
            cleaned_dict["question"] = ("Should " + qs) if qs else p_title_for_question

        extra = data_dict.get("profile", {}).get("extra", {}) if isinstance(data_dict, dict) else {}

        # 2) parse known 3 HTML fields
        cleaned_dict["parsed_known_html"] = {}
        for k in ("oneRowSource", "ietdPrintout", "sofSource"):
            raw_html = extra.get(k)
            if isinstance(raw_html, str) and raw_html.strip():
                doc = self._ensure_document(raw_html)
                cleaned_dict["parsed_known_html"][k] = self.parser.parse(doc)
            else:
                cleaned_dict["parsed_known_html"][k] = None

        # 3) traverse whole raw dict and parse other html strings
        cleaned_dict["extra_html_parsed"] = {}
        seen_hashes: Set[int] = set()

        for path, value in self._iter_paths(data_dict):
            if not isinstance(value, str):
                continue
            if self._is_excluded_path(path, excluded_html_keys):
                continue
            if not self._looks_like_html(value):
                continue

            h = hash(value)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            try:
                doc = self._ensure_document(value)
                cleaned_dict["extra_html_parsed"][path] = self.parser.parse(doc)
            except Exception as e:
                cleaned_dict["extra_html_parsed"][path] = {"_error": str(e)}

        return cleaned_dict

    # -----------------------------
    # IO helpers
    # -----------------------------
    def _save_json(self, obj: Any, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

    def _fetch_profile_xhr(self, tab, profile_url: str, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        在单独 tab 中打开 profile_url，并监听该 profile_id 对应的 xhr。
        返回 response.body（dict）或 None
        """
        tab.listen.start(targets=profile_id, res_type="xhr")
        tab.get(profile_url)
        res = tab.listen.wait(timeout=self.timeout)
        if not res:
            return None
        return res.response.body

    # -----------------------------
    # pagination helpers (尽量稳健)
    # -----------------------------
    def _click_next_page(self, tab) -> bool:
        """
        点击 results-pagination 里的 nextArrow 按钮翻页。
        成功翻到下一页返回 True；否则 False（末页/不可点/点击无变化）。
        """
        # 当前页号（用于判断是否真的翻页成功）
        cur_btn = tab.ele("css:div.results-pagination button.pageButton.currentPage", timeout=2)
        cur_page = (cur_btn.text or "").strip() if cur_btn else ""

        # 精确找 nextArrow 按钮：button.pageButton 里包含 img[src*='nextArrow']
        next_btn = tab.ele(
            "css:div.results-pagination button.pageButton:has(img[src*='nextArrow'])",
            timeout=2
        )
        if not next_btn:
            return False

        # 判断是否 disabled
        disabled_attr = next_btn.attr("disabled")
        cls = (next_btn.attr("class") or "").lower()
        if disabled_attr is not None or "disabled" in cls:
            return False

        # 点击翻页
        next_btn.click()

        # 等待 currentPage 改变；没改变视为末页/点击无效
        for _ in range(40):  # 最多等约 4 秒
            time.sleep(0.1)
            cur_btn2 = tab.ele("css:div.results-pagination button.pageButton.currentPage", timeout=1)
            cur_page2 = (cur_btn2.text or "").strip() if cur_btn2 else ""
            if cur_page2 and cur_page2 != cur_page:
                return True

        return False

    # -----------------------------
    # crawl
    # -----------------------------
    def crawl(self):
        tab = self.browser.latest_tab

        for url in self.start_urls:
            print(f"\n[*] 开始搜索页: {url}")
            tab.get(url)

            page = 1
            while True:
                print(f"[*] 正在处理第 {page} 页 ...")

                papers = tab.eles("@class=profile")
                if not papers:
                    print("[!] 未找到 profile 列表元素，可能页面结构变化。")
                    break

                for paper in papers:
                    p_url = paper.child().attr("href")
                    p_name = (paper.child().text or "").strip()

                    if not p_url:
                        continue

                    # 用 title 做文件名（要求小写）
                    clean_title = self.clean_p_title(p_name)
                    if clean_title in self.seen_titles:
                        print(f"[-] 跳过重复: {clean_title}")
                        continue

                    profile_id = p_url.split("/")[-1].strip()
                    if not profile_id:
                        continue

                    print(f"[+] 抓取: {p_name} -> {clean_title}")

                    newtab = self.browser.new_tab()
                    try:
                        rawdict = self._fetch_profile_xhr(newtab, p_url, profile_id)
                        if not rawdict:
                            print(f"[!] 未捕获到XHR: {clean_title}")
                            continue

                        # 1) 保存 raw xhr 备份
                        raw_path = os.path.join(self.raw_dir, f"{clean_title}.raw.json")
                        self._save_json(rawdict, raw_path)

                        # 2) 结构化清洗
                        cleaned = self.newclean(rawdict, p_title_for_question=p_name or clean_title)

                        # 3) 保存 cleaned json
                        out_path = os.path.join(self.output_dir, f"{clean_title}.json")
                        self._save_json(cleaned, out_path)

                        # 标记已处理（只要成功保存，就算爬取成功）
                        self.seen_titles.add(clean_title)

                        print(f"    [OK] saved raw: {raw_path}")
                        print(f"    [OK] saved cleaned: {out_path}")

                    except Exception as e:
                        print(f"[!] 处理失败 {clean_title}: {e}")
                    finally:
                        try:
                            newtab.close()
                        except Exception:
                            pass

                # 翻页
                page += 1
                if not self._click_next_page(tab):
                    print("[*] 到达末页或无法翻页，结束该搜索。")
                    break


if __name__ == "__main__":
    TARGET_URLS = [
        'https://guidelines.gradepro.org/search/%22Should%22?type=_all',
        'https://guidelines.gradepro.org/search/%22or%22?type=_all',
        'https://guidelines.gradepro.org/search/%22vs.%22?type=_all',
        'https://guidelines.gradepro.org/search/%22and%22?type=_all',
        'https://guidelines.gradepro.org/search/%22a%22?type=_all',
    ]

    crawler = WebsiteCrawler(start_urls=TARGET_URLS, output_dir="guidelines_data", raw_dir="guidelines_raw", timeout=25)
    try:
        crawler.crawl()
    except KeyboardInterrupt:
        print("\n[!] 用户中断操作")
    finally:
        print("\n[*] 正在安全退出...")
        crawler.browser.quit()