# -*- coding: utf-8 -*-
import re
from copy import deepcopy
from io import StringIO

import pandas as pd
from lxml import html


class GDTHtmlParser:
    """
    解析 GRADEpro / Guideline Development Tool printout HTML：
    - 只输出顶层 table（嵌套表嵌入单元格）
    - 识别并专门解析 Assessment(Evidence profile) 大表为 sections 结构
    - 识别 Question/Question__2 两列表并提取为 pico dict（并从 tablematrix 移除）
    - 不输出 xpath
    - 修改点：嵌套小表格使用 pandas.read_html() 解析并替换原位置
    """

    def __init__(self):
        pass

    # ------------------------
    # public API
    # ------------------------
    def parse(self, html_text: str) -> dict:
        html_text = self._maybe_unescape_html_text(html_text)
        root, tree = self._parse_document(html_text)

        top_tables = root.xpath(".//table[not(ancestor::table)]")
        tablematrix = [self._extract_table_object(t, tree) for t in top_tables]

        pico = {}
        filtered = []
        for t in tablematrix:
            if self._is_question_kv_table(t):
                pico = self._table_to_pico(t)
                continue
            filtered.append(t)

        return {"pico": pico, "tablematrix": filtered}

    # ------------------------
    # basic utils
    # ------------------------
    def _norm_text(self, s: str) -> str:
        return re.sub(r"\s+", " ", s or "").strip()

    def _maybe_unescape_html_text(self, s: str) -> str:
        if s is None:
            return ""
        if '\\"' in s or "\\n" in s or "\\t" in s:
            s = s.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")
        return s

    def _parse_document(self, html_text: str):
        parser = html.HTMLParser(encoding="utf-8", remove_comments=False)
        root = html.fromstring(html_text, parser=parser)
        tree = root.getroottree()
        return root, tree

    def _parse_span_int(self, value, default: int = 1) -> int:
        if value is None:
            return default
        s = str(value).strip()
        if not s:
            return default
        s = s.strip('\'"')
        try:
            return int(s)
        except Exception:
            m = re.search(r"\d+", s)
            return int(m.group(0)) if m else default

    def _text_preserving_br(self, el) -> str:
        if el is None:
            return ""
        parts = []
        if el.text:
            parts.append(el.text)
        for node in el.iter():
            if node is el:
                continue
            if isinstance(node.tag, str) and node.tag.lower() == "br":
                parts.append("\n")
            if node.text:
                parts.append(node.text)
            if node.tail:
                parts.append(node.tail)
        text = "".join(parts)
        text = text.replace("\r\n", "\n")
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _remove_descendant_tables(self, el):
        tmp = deepcopy(el)
        for t in tmp.xpath(".//table"):
            p = t.getparent()
            if p is not None:
                p.remove(t)
        return tmp

    def _is_direct_child_table(self, nt, outer_table) -> bool:
        anc = nt.xpath("ancestor::table")
        if not anc:
            return False
        return anc[-1] is outer_table

    def _get_direct_nested_tables(self, cell, outer_table):
        nested = []
        for nt in cell.xpath(".//table"):
            if self._is_direct_child_table(nt, outer_table):
                nested.append(nt)
        return nested

    # ------------------------
    # NEW: nested small table via pandas.read_html
    # ------------------------
    def _flatten_colname(self, col) -> str:
        """
        pandas MultiIndex/tuple 列名扁平化：用 ' / ' 分隔，保留层级结构的可读性。
        """
        if isinstance(col, tuple):
            parts = [self._norm_text(str(x)) for x in col if x is not None and self._norm_text(str(x))]
            return " / ".join(parts) if parts else ""
        return self._norm_text(str(col))

    def _dedup_headers(self, headers):
        """
        对重复列名加 __2/__3，保持 key 唯一。
        """
        seen = {}
        out = []
        for h in headers:
            h = h if h else ""
            if not h:
                out.append("")
                continue
            if h not in seen:
                seen[h] = 1
                out.append(h)
            else:
                seen[h] += 1
                out.append(f"{h}__{seen[h]}")
        return out

    def _pandas_parse_table_el(self, table_el) -> dict:
        """
        将一个 <table> 用 pandas.read_html 解析，返回可嵌入整体 dict 的结构。
        """
        table_html = html.tostring(table_el, encoding="unicode", with_tail=False)
        dfs = pd.read_html(StringIO(table_html), flavor="lxml")

        parsed_tables = []
        for df in dfs:
            # NaN/NA -> None
            df = df.where(pd.notna(df), None)

            # 扁平化 columns（MultiIndex -> tuple -> "a / b"）
            if isinstance(df.columns, pd.MultiIndex):
                flat_cols = [self._flatten_colname(t) for t in df.columns.to_list()]
            else:
                # 有些场景 df.columns 里也可能直接是 tuple
                flat_cols = [self._flatten_colname(c) for c in df.columns.tolist()]

            flat_cols = self._dedup_headers(flat_cols)

            # 空列名补 col_n
            for i, c in enumerate(flat_cols):
                if not c:
                    flat_cols[i] = f"col_{i+1}"

            df.columns = flat_cols

            parsed_tables.append({
                "_type": "pandas_table",
                "headers": flat_cols,
                "rows": df.to_dict(orient="records")
            })

        if len(parsed_tables) == 1:
            return parsed_tables[0]
        return {"_type": "pandas_tables", "tables": parsed_tables}

    def _parse_nested_table(self, nt, tree):
        """
        嵌套表优先用 pandas 解析；失败则回退到原解析逻辑。
        """
        try:
            return self._pandas_parse_table_el(nt)
        except Exception:
            # fallback：仍保持原先解析方式
            return self._extract_table_object(nt, tree)

    # ------------------------
    # Special: Assessment / Evidence profile big table
    # ------------------------
    def _looks_like_assessment_ep_table(self, table_el) -> bool:
        if not table_el.xpath("./tbody[contains(@class,'expanded')]"):
            return False
        if not table_el.xpath(".//tr[contains(@class,'assessment-section__header')]"):
            return False
        if not table_el.xpath(".//tr[contains(@class,'ep-section-row')]"):
            return False
        if not table_el.xpath(".//td[contains(@class,'ep-cell') and contains(@class,'judgement')]"):
            return False
        return True

    def _parse_judgement_cell(self, td) -> dict:
        sel = td.xpath(".//span[contains(@class,'checked-marker')]/following-sibling::span[contains(@class,'option-label')][1]/text()")
        selected = self._norm_text(sel[0]) if sel else None

        items = []
        for lab in td.xpath(".//fieldset//label"):
            marker = self._norm_text("".join(
                lab.xpath(".//span[contains(@class,'checked-marker') or contains(@class,'unchecked-marker')]/text()")
            ))
            opt = self._norm_text("".join(lab.xpath(".//span[contains(@class,'option-label')]/text()")))
            if marker or opt:
                items.append(f"{marker} {opt}".strip())

        judgement_raw = "".join(items) if items else self._norm_text(self._text_preserving_br(td))
        return {"judgement_raw": judgement_raw, "judgement_selected": selected}

    def _parse_cell_with_nested_tables(self, td, outer_table, tree):
        """
        修改点：嵌套表用 pandas 解析后嵌入
        """
        tmp = self._remove_descendant_tables(td)
        own_text = self._norm_text(self._text_preserving_br(tmp))

        nested_tables = [self._parse_nested_table(nt, tree) for nt in self._get_direct_nested_tables(td, outer_table)]
        if nested_tables:
            if own_text:
                return {"text": own_text, "tables": nested_tables}
            return nested_tables[0] if len(nested_tables) == 1 else {"tables": nested_tables}
        return own_text

    def _parse_assessment_ep_table(self, table_el, tree) -> dict:
        sections = []
        for tbody in table_el.xpath("./tbody[contains(@class,'expanded')]"):
            h2 = tbody.xpath(".//tr[contains(@class,'assessment-section__header')]//h2")
            criterion = self._norm_text(h2[0].text_content()) if h2 else None

            subtitle = tbody.xpath(".//tr[contains(@class,'assessment-section__header')]//p[contains(@class,'subtitle')]")
            question = self._norm_text(subtitle[0].text_content()) if subtitle else None

            content_trs = tbody.xpath("./tr[contains(@class,'ep-section-row')]")
            if not content_trs:
                continue
            content_tr = content_trs[0]

            td_j = content_tr.xpath("./td[contains(@class,'judgement')]")
            td_r = content_tr.xpath("./td[contains(@class,'research-evidences')]")
            td_a = content_tr.xpath("./td[contains(@class,'additional-considerations')]")

            td_j = td_j[0] if td_j else None
            td_r = td_r[0] if td_r else None
            td_a = td_a[0] if td_a else None

            judgement_info = self._parse_judgement_cell(td_j) if td_j is not None else {"judgement_raw": "", "judgement_selected": None}
            research_val = self._parse_cell_with_nested_tables(td_r, table_el, tree) if td_r is not None else ""
            add_val = self._parse_cell_with_nested_tables(td_a, table_el, tree) if td_a is not None else ""

            sections.append({
                "criterion": criterion,
                "question": question,
                **judgement_info,
                "research_evidence": research_val,
                "additional_considerations": add_val,
            })

        return {
            "_type": "assessment_table",
            "class": table_el.get("class") or "",
            "sections": sections
        }

    # ------------------------
    # Generic table parser (for other tables + nested tables)
    # ------------------------
    def _merge_header_rows(self, header_rows):
        if not header_rows:
            return []
        cols = len(header_rows[0])
        merged = []
        for c in range(cols):
            parts = []
            for r in header_rows:
                v = r[c] if c < len(r) else ""
                if isinstance(v, dict):
                    v = v.get("text", "")
                v = self._norm_text(v) if isinstance(v, str) else ""
                if v:
                    parts.append(v)
            merged.append(" / ".join(parts) if parts else "")

        seen = {}
        out = []
        for h in merged:
            if not self._norm_text(h):
                out.append("")
                continue
            if h not in seen:
                seen[h] = 1
                out.append(h)
            else:
                seen[h] += 1
                out.append(f"{h}__{seen[h]}")
        return out

    def _detect_headers_and_body(self, table_el, grid, original_trs):
        thead_trs = table_el.xpath("./thead//tr")
        if thead_trs:
            n = len(thead_trs)
            return grid[:n], grid[n:]

        n = 0
        for tr in original_trs:
            if tr.xpath("./th"):
                n += 1
            else:
                break
        if n > 0:
            return grid[:n], grid[n:]

        if grid:
            first = grid[0]

            def non_empty(x):
                if isinstance(x, dict):
                    x = x.get("text", "")
                return bool(self._norm_text(x)) if isinstance(x, str) else False

            if len(first) >= 2 and sum(non_empty(x) for x in first) >= max(2, int(0.6 * len(first))):
                return [first], grid[1:]

        return [], grid

    def _grid_to_records(self, headers, body_rows):
        if not body_rows:
            return [], headers
        n_cols = max(len(r) for r in body_rows)

        if not headers:
            headers = [f"col_{i+1}" for i in range(n_cols)]
        else:
            if len(headers) < n_cols:
                headers = headers + [""] * (n_cols - len(headers))
            for i in range(n_cols):
                if i >= len(headers) or not self._norm_text(headers[i]):
                    headers[i] = f"col_{i+1}"

        records = []
        for row in body_rows:
            row = list(row) + [""] * (n_cols - len(row))
            records.append({headers[i]: row[i] for i in range(n_cols)})

        return records, headers

    def _table_to_grid(self, table_el, tree):
        """
        修改点：嵌套表用 pandas 解析后嵌入（与 assessment 表一致）
        """
        grid = []
        trs = table_el.xpath(".//tr")

        for tr in trs:
            r = len(grid)
            grid.append([])
            c = 0

            for cell in tr.xpath("./th|./td"):
                while c < len(grid[r]) and grid[r][c] is not None:
                    c += 1

                rowspan = max(1, self._parse_span_int(cell.get("rowspan"), 1))
                colspan = max(1, self._parse_span_int(cell.get("colspan"), 1))

                tmp = self._remove_descendant_tables(cell)
                own_text = self._norm_text(self._text_preserving_br(tmp))

                nested = [self._parse_nested_table(nt, tree) for nt in self._get_direct_nested_tables(cell, outer_table=table_el)]
                if nested:
                    cell_value = {"text": own_text, "tables": nested} if own_text else (nested[0] if len(nested) == 1 else {"tables": nested})
                else:
                    cell_value = own_text

                need_len = c + colspan
                if len(grid[r]) < need_len:
                    grid[r].extend([None] * (need_len - len(grid[r])))

                for k in range(colspan):
                    grid[r][c + k] = cell_value

                if rowspan > 1:
                    for rr in range(1, rowspan):
                        tr_idx = r + rr
                        while len(grid) <= tr_idx:
                            grid.append([])
                        if len(grid[tr_idx]) < need_len:
                            grid[tr_idx].extend([None] * (need_len - len(grid[tr_idx])))
                        for k in range(colspan):
                            if grid[tr_idx][c + k] is None:
                                grid[tr_idx][c + k] = None

                c += colspan

        max_cols = max((len(r) for r in grid), default=0)
        for r in grid:
            if len(r) < max_cols:
                r.extend([None] * (max_cols - len(r)))
        grid = [[("" if x is None else x) for x in r] for r in grid]
        return grid, trs

    def _parse_summary_of_judgements(self, table_el, tree):
        rows = []
        for tr in table_el.xpath("./tbody/tr"):
            criterion = self._norm_text("".join(tr.xpath("./td[contains(@class,'section-name')]//text()")))
            options = []
            selected = None
            for td in tr.xpath("./td[contains(@class,'option-text')]"):
                txt = self._norm_text(td.text_content())
                cls = (td.get("class") or "").split()
                checked = "checked" in cls
                empty = "empty" in cls
                options.append({"text": txt, "checked": checked, "empty": empty})
                if checked:
                    selected = txt
            rows.append({"criterion": criterion, "options": options, "selected": selected})

        return {
            "_type": "summary-of-judgements",
            "class": table_el.get("class") or "",
            "rows": rows
        }

    def _extract_table_object(self, table_el, tree):
        t_class = table_el.get("class") or ""

        if self._looks_like_assessment_ep_table(table_el):
            return self._parse_assessment_ep_table(table_el, tree)

        if "summary-of-judgements" in t_class:
            return self._parse_summary_of_judgements(table_el, tree)

        grid, trs = self._table_to_grid(table_el, tree)
        header_rows, body_rows = self._detect_headers_and_body(table_el, grid, trs)
        headers = self._merge_header_rows(header_rows)
        records, headers = self._grid_to_records(headers, body_rows)

        return {
            "_type": "table",
            "class": t_class,
            "headers": headers,
            "rows": records
        }

    # ------------------------
    # Post-process: PICO from the "Question / Question__2" table
    # ------------------------
    def _is_question_kv_table(self, table_obj: dict) -> bool:
        if not isinstance(table_obj, dict):
            return False
        if table_obj.get("_type") != "table":
            return False
        headers = table_obj.get("headers") or []
        if len(headers) != 2:
            return False
        return headers[0] == "Question" and str(headers[1]).startswith("Question__")

    def _table_to_pico(self, table_obj: dict) -> dict:
        headers = table_obj["headers"]
        h1, h2 = headers[0], headers[1]
        pico = {}

        for row in table_obj.get("rows", []):
            k = self._norm_text(row.get(h1, ""))
            v = row.get(h2, "")
            if isinstance(v, str):
                v = self._norm_text(v)

            if not k:
                continue

            if isinstance(v, str) and k == v:
                pico.setdefault("Question", k)
                continue

            if k.endswith(":"):
                key = self._norm_text(k[:-1])
                if key:
                    pico[key] = v
                continue

            pico[k] = v

        return pico