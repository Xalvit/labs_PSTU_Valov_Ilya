#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import html
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Node:
    comment: str = ""
    left_ext: float = 0.0
    right_ext: float = 0.0
    height: float = 0.0


@dataclass
class BlockNode(Node):
    kind: str = "rect"  # "oval", "rect", "io", "func_header"
    text: str = ""
    box_w: float = 0.0
    box_h: float = 0.0


@dataclass
class IfNode(Node):
    condition: str = ""
    true_branch: List[Node] = field(default_factory=list)
    false_branch: List[Node] = field(default_factory=list)
    diamond_w: float = 0.0
    diamond_h: float = 0.0
    top_pad: float = 0.0
    offset_l: float = 0.0
    offset_r: float = 0.0
    branch_h: float = 0.0


@dataclass
class LoopNode(Node):
    loop_kind: str = "while"  # "while" (ромб) или "for" (шестиугольник)
    header: str = ""
    body: List[Node] = field(default_factory=list)
    shape_w: float = 0.0
    shape_h: float = 0.0
    hex_tip_w: float = 0.0
    top_pad: float = 0.0
    body_h: float = 0.0
    left_back_offset: float = 0.0
    right_exit_offset: float = 0.0


@dataclass
class SwitchCaseItem:
    label: str = ""
    statements: List[BlockNode] = field(default_factory=list)
    comment: str = ""
    falls_through: bool = False
    diamond_w: float = 0.0
    diamond_h: float = 0.0
    top_pad: float = 0.0
    row_h: float = 0.0
    row_w: float = 0.0


@dataclass
class SwitchNode(Node):
    header_text: str = ""
    cases: List[SwitchCaseItem] = field(default_factory=list)
    header_block: Optional[BlockNode] = None
    max_diamond_w: float = 0.0
    collector_x_offset: float = 0.0


@dataclass
class FuncNode(Node):
    signature: str = ""
    body: List[Node] = field(default_factory=list)
    is_main: bool = False
    header_node: Optional[BlockNode] = None


@dataclass
class ProgramAST:
    preamble: List[str] = field(default_factory=list)
    globals_before: List[Node] = field(default_factory=list)


class CppFlowParser:
    def __init__(self, source: str):
        self.source = source

    def parse(self) -> ProgramAST:
        ast = ProgramAST()
        lines = self.source.splitlines()
        clean_lines = []
        in_preamble = True

        for line in lines:
            raw = line.strip()
            if not raw:
                clean_lines.append(line)
                continue
            if in_preamble and (raw.startswith("#") or re.match(r"^using\s+namespace\b", raw)):
                ast.preamble.append(raw)
            else:
                if not raw.startswith("//") and not raw.startswith("/*"):
                    in_preamble = False
                clean_lines.append(line)

        remaining_code = "\n".join(clean_lines)
        tokens = self._tokenize_top_level(remaining_code)
        ast.globals_before = self._parse_items(tokens, in_main=False, top_level=True)
        return ast

    def _extract_comments(self, text: str, preserve_newlines: bool = False) -> Tuple[str, str]:
        comments = []

        def repl_block(m):
            comments.append(m.group(0).strip())
            return " "

        def repl_line(m):
            comments.append(m.group(0).strip())
            return ""

        no_block = re.sub(r"/\*.*?\*/", repl_block, text, flags=re.DOTALL)
        no_line = re.sub(r"//[^\n]*", repl_line, no_block)

        if preserve_newlines:
            cleaned_lines = [
                " ".join(ln.strip().split())
                for ln in no_line.splitlines()
                if ln.strip()
            ]
            clean_code = "\n".join(cleaned_lines)
        else:
            clean_code = " ".join(no_line.strip().split())

        return clean_code, "\n".join(comments)

    def _find_matching(self, s: str, start_idx: int, open_ch: str, close_ch: str) -> int:
        depth = 0
        in_str = False
        str_ch = ""
        i = start_idx
        while i < len(s):
            ch = s[i]
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == str_ch:
                    in_str = False
            else:
                if ch in ('"', "'"):
                    in_str = True
                    str_ch = ch
                elif s[i:i+2] == "//":
                    nl = s.find("\n", i)
                    i = len(s) if nl == -1 else nl
                elif s[i:i+2] == "/*":
                    end = s.find("*/", i + 2)
                    i = len(s) if end == -1 else end + 1
                elif ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth == 0:
                        return i
            i += 1
        return len(s) - 1

    def _tokenize_top_level(self, code: str) -> List[str]:
        statements = []
        i = 0
        n = len(code)
        buf = []

        while i < n:
            if not buf and code[i].isspace():
                i += 1
                continue

            if not buf and code[i] == "#":
                nl = code.find("\n", i)
                if nl == -1:
                    statements.append(code[i:].strip())
                    break
                statements.append(code[i:nl].strip())
                i = nl + 1
                continue

            if code[i:i+2] == "//":
                nl = code.find("\n", i)
                if nl == -1:
                    buf.append(code[i:])
                    break
                buf.append(code[i:nl+1])
                i = nl + 1
                continue

            if code[i:i+2] == "/*":
                end = code.find("*/", i + 2)
                if end == -1:
                    buf.append(code[i:])
                    break
                buf.append(code[i:end+2])
                i = end + 2
                continue

            if code[i] in ('"', "'"):
                quote = code[i]
                buf.append(quote)
                i += 1
                while i < n:
                    buf.append(code[i])
                    if code[i] == "\\":
                        i += 1
                        if i < n:
                            buf.append(code[i])
                    elif code[i] == quote:
                        i += 1
                        break
                    i += 1
                continue

            if code[i] == "(":
                end_p = self._find_matching(code, i, "(", ")")
                buf.append(code[i:end_p+1])
                i = end_p + 1
                continue

            if code[i] == "{":
                end_b = self._find_matching(code, i, "{", "}")
                buf.append(code[i:end_b+1])
                i = end_b + 1

                temp_i = i
                while temp_i < n and code[temp_i].isspace():
                    temp_i += 1

                if temp_i < n and code[temp_i] == ";":
                    i = temp_i
                    continue

                if re.match(r"^else\b", code[temp_i:]):
                    i = temp_i
                    continue

                stmt = "".join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
                continue

            if code[i] == ";":
                buf.append(";")
                i += 1

                current_text = "".join(buf).strip()
                stripped_no_comm = re.sub(r"//[^\n]*|/\*.*?\*/", "", current_text).strip()
                if re.match(r"^if\s*\(", stripped_no_comm):
                    temp_i = i
                    while temp_i < n and code[temp_i].isspace():
                        temp_i += 1
                    if re.match(r"^else\b", code[temp_i:]):
                        i = temp_i
                        continue

                while i < n and code[i] in (" ", "\t"):
                    i += 1
                if code[i:i+2] == "//":
                    nl = code.find("\n", i)
                    if nl == -1:
                        buf.append(" " + code[i:])
                        i = n
                    else:
                        buf.append(" " + code[i:nl])
                        i = nl + 1
                elif code[i:i+2] == "/*":
                    end = code.find("*/", i + 2)
                    if end != -1:
                        buf.append(" " + code[i:end+2])
                        i = end + 2

                stmt = "".join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
                continue

            buf.append(code[i])
            i += 1

        leftover = "".join(buf).strip()
        if leftover:
            statements.append(leftover)
        return statements

    def _parse_branch_body(self, raw_body: str, in_main: bool) -> List[Node]:
        raw_body = raw_body.strip()
        if not raw_body:
            return []
        if raw_body.startswith("{") and raw_body.endswith("}"):
            inner = raw_body[1:-1].strip()
            tokens = self._tokenize_top_level(inner)
            return self._parse_items(tokens, in_main=in_main, top_level=False)
        tokens = self._tokenize_top_level(raw_body)
        return self._parse_items(tokens, in_main=in_main, top_level=False)

    def _find_statement_end(self, s: str) -> int:
        i = 0
        n = len(s)
        while i < n:
            if s[i] == "(":
                i = self._find_matching(s, i, "(", ")") + 1
            elif s[i] == "{":
                i = self._find_matching(s, i, "{", "}") + 1
            elif s[i] == ";":
                return i
            else:
                i += 1
        return n - 1

    def _strip_leading_comments(self, text: str) -> Tuple[str, List[str]]:
        comments = []
        s = text.strip()
        while True:
            if s.startswith("//"):
                nl = s.find("\n")
                if nl == -1:
                    comments.append(s.strip())
                    s = ""
                    break
                comments.append(s[:nl].strip())
                s = s[nl+1:].strip()
            elif s.startswith("/*"):
                end = s.find("*/")
                if end == -1:
                    comments.append(s.strip())
                    s = ""
                    break
                comments.append(s[:end+2].strip())
                s = s[end+2:].strip()
            else:
                break
        return s, comments

    def _parse_if(self, text: str, in_main: bool) -> IfNode:
        s, leading_comments = self._strip_leading_comments(text)
        open_p = s.find("(")
        close_p = self._find_matching(s, open_p, "(", ")")
        cond_raw = s[:close_p+1]
        cond_clean, cond_comm = self._extract_comments(cond_raw)
        if cond_comm:
            leading_comments.append(cond_comm)

        rest = s[close_p+1:].strip()
        rest, post_comments = self._strip_leading_comments(rest)
        if post_comments:
            leading_comments.extend(post_comments)

        false_part = ""
        if rest.startswith("{"):
            end_b = self._find_matching(rest, 0, "{", "}")
            true_part = rest[:end_b+1]
            after_true = rest[end_b+1:].strip()
        else:
            semi_pos = self._find_statement_end(rest)
            true_part = rest[:semi_pos+1]
            after_true = rest[semi_pos+1:].strip()
            after_true, inline_comms = self._strip_leading_comments(after_true)
            if inline_comms and not after_true:
                true_part = true_part + " " + " ".join(inline_comms)

        after_true, _ = self._strip_leading_comments(after_true)
        if re.match(r"^else\b", after_true):
            false_part = re.sub(r"^else\b", "", after_true, count=1).strip()

        true_nodes = self._parse_branch_body(true_part, in_main=in_main)
        false_nodes = self._parse_branch_body(false_part, in_main=in_main) if false_part else []

        return IfNode(
            condition=cond_clean,
            true_branch=true_nodes,
            false_branch=false_nodes,
            comment="\n".join(leading_comments)
        )

    def _parse_loop(self, text: str, in_main: bool) -> LoopNode:
        s, leading_comments = self._strip_leading_comments(text)
        loop_kind = "for" if re.match(r"^for\b", s) else "while"

        open_p = s.find("(")
        close_p = self._find_matching(s, open_p, "(", ")")
        hdr_raw = s[:close_p+1]
        hdr_clean, hdr_comm = self._extract_comments(hdr_raw)
        if hdr_comm:
            leading_comments.append(hdr_comm)

        rest = s[close_p+1:].strip()
        rest, post_comments = self._strip_leading_comments(rest)
        if post_comments:
            leading_comments.extend(post_comments)

        body_nodes = self._parse_branch_body(rest, in_main=in_main)
        return LoopNode(
            loop_kind=loop_kind,
            header=hdr_clean,
            body=body_nodes,
            comment="\n".join(leading_comments)
        )

    def _parse_switch(self, text: str) -> SwitchNode:
        s, leading_comments = self._strip_leading_comments(text)
        open_p = s.find("(")
        close_p = self._find_matching(s, open_p, "(", ")")
        header_clean, header_comm = self._extract_comments(s[:close_p+1])
        if header_comm:
            leading_comments.append(header_comm)

        rest = s[close_p+1:].strip()
        rest, post_hdr_comments = self._strip_leading_comments(rest)
        if post_hdr_comments:
            leading_comments.extend(post_hdr_comments)

        if rest.startswith("{") and rest.endswith("}"):
            inner = rest[1:-1].strip()
        else:
            inner = rest

        pattern = re.compile(r"\b(case\s+[^:]+:|default\s*:)")
        matches = list(pattern.finditer(inner))
        cases: List[SwitchCaseItem] = []

        for idx, m in enumerate(matches):
            label_raw = " ".join(m.group(1).strip().split())
            start_pos = m.end()
            end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(inner)
            body_chunk = inner[start_pos:end_pos].strip()

            if body_chunk.startswith("{") and body_chunk.endswith("}"):
                body_chunk = body_chunk[1:-1].strip()

            raw_stmts = self._tokenize_top_level(body_chunk)
            stmt_blocks: List[BlockNode] = []
            case_comments: List[str] = []

            for st in raw_stmts:
                c_clean, c_comm = self._extract_comments(st)
                if not c_clean:
                    if c_comm:
                        if stmt_blocks:
                            stmt_blocks[-1].comment = (
                                (stmt_blocks[-1].comment + "\n" + c_comm).strip()
                            )
                        else:
                            case_comments.append(c_comm)
                    continue
                kind = (
                    "io"
                    if re.search(r"\b(cin|cout|std::cin|std::cout|printf|scanf|getline)\b", c_clean)
                    else "rect"
                )
                stmt_blocks.append(BlockNode(kind=kind, text=c_clean, comment=c_comm))

            # Определяем, проваливается ли этот case в следующий (отсутствует break / return / exit)
            has_terminator = any(
                re.match(r"^(break|return|exit|std::exit|throw)\b", b.text.strip())
                for b in stmt_blocks
            )
            is_last_case = (idx == len(matches) - 1)
            falls_through = (not has_terminator) and (not is_last_case)

            cases.append(
                SwitchCaseItem(
                    label=label_raw,
                    statements=stmt_blocks,
                    comment="\n".join(case_comments),
                    falls_through=falls_through
                )
            )

        return SwitchNode(
            header_text=header_clean,
            cases=cases,
            comment="\n".join(leading_comments)
        )

    def _parse_items(self, tokens: List[str], in_main: bool, top_level: bool) -> List[Node]:
        nodes: List[Node] = []
        pending_comment = ""

        for tok in tokens:
            s_clean, lead_comms = self._strip_leading_comments(tok)
            if lead_comms:
                pending_comment = (pending_comment + "\n" + "\n".join(lead_comms)).strip()

            if not s_clean:
                continue

            if re.match(r"^if\s*\(", s_clean):
                node = self._parse_if(s_clean, in_main=in_main)
                if pending_comment:
                    node.comment = (pending_comment + "\n" + node.comment).strip()
                    pending_comment = ""
                nodes.append(node)
                continue

            if re.match(r"^(for|while)\s*\(", s_clean):
                node = self._parse_loop(s_clean, in_main=in_main)
                if pending_comment:
                    node.comment = (pending_comment + "\n" + node.comment).strip()
                    pending_comment = ""
                nodes.append(node)
                continue

            if re.match(r"^switch\s*\(", s_clean):
                node = self._parse_switch(s_clean)
                if pending_comment:
                    node.comment = (pending_comment + "\n" + node.comment).strip()
                    pending_comment = ""
                nodes.append(node)
                continue

            if top_level and "{" in s_clean and not s_clean.endswith(";"):
                brace_idx = s_clean.find("{")
                header_raw = s_clean[:brace_idx].strip()
                body_raw = s_clean[brace_idx:].strip()
                header_clean, header_comm = self._extract_comments(header_raw)

                if re.search(r"\b\w+\s*\([^)]*\)\s*$", header_clean):
                    is_main_func = bool(re.search(r"\bmain\s*\(", header_clean))
                    body_nodes = self._parse_branch_body(body_raw, in_main=is_main_func)
                    full_comm = "\n".join(filter(None, [pending_comment, header_comm]))
                    pending_comment = ""
                    nodes.append(FuncNode(
                        signature=header_clean,
                        body=body_nodes,
                        is_main=is_main_func,
                        comment=full_comm
                    ))
                    continue

            is_multiline_struct = bool(re.match(r"^(struct|class|enum)\b", s_clean)) or (
                "\n" in s_clean and "{" in s_clean
            )
            code_clean, comm = self._extract_comments(s_clean, preserve_newlines=is_multiline_struct)
            full_comm = "\n".join(filter(None, [pending_comment, comm]))
            pending_comment = ""

            if re.search(r"\b(cin|cout|std::cin|std::cout|printf|scanf|getline)\b", code_clean):
                kind = "io"
            elif in_main and re.match(r"^return\b", code_clean):
                kind = "oval"
            else:
                kind = "rect"

            nodes.append(BlockNode(kind=kind, text=code_clean, comment=full_comm))

        return nodes


class FlowchartSVGRenderer:
    FONT_SIZE = 14
    CHAR_W = 8.4
    LINE_H = 20.0
    PAD_X = 18.0
    PAD_Y = 12.0
    V_GAP = 38.0
    H_GAP = 50.0
    IO_SLANT = 14.0
    FUNC_STRIPE = 10.0
    SWITCH_FALL_SHOULDER = 52.0
    SWITCH_TRUE_GAP = 88.0
    SWITCH_STMT_GAP = 30.0
    SWITCH_CASE_V_GAP = 44.0
    SWITCH_BOTTOM_GAP = 52.0

    def __init__(self, ast: ProgramAST):
        self.ast = ast
        self.svg_elements: List[str] = []

    def _measure_text(self, text: str) -> Tuple[float, float, List[str]]:
        lines = text.splitlines() if text else [""]
        max_chars = max(len(line) for line in lines)
        w = max(max_chars * self.CHAR_W, 40.0)
        h = len(lines) * self.LINE_H
        return w, h, lines

    def _measure_comment_width(self, comment: str) -> float:
        if not comment:
            return 0.0
        w, _, _ = self._measure_text(comment)
        return w + 35.0

    def _measure_node(self, node: Node, allow_center_shift: bool = False):
        comm_w = self._measure_comment_width(node.comment)

        if isinstance(node, BlockNode):
            tw, th, _ = self._measure_text(node.text)
            if node.kind == "io":
                node.box_w = tw + 2 * self.PAD_X + 2 * self.IO_SLANT
            elif node.kind == "func_header":
                node.box_w = tw + 2 * self.PAD_X + 2 * self.FUNC_STRIPE
            elif node.kind == "oval":
                node.box_w = tw + 2 * self.PAD_X + 16.0
            else:
                node.box_w = tw + 2 * self.PAD_X

            node.box_h = max(th + 2 * self.PAD_Y, 40.0)
            node.left_ext = node.box_w / 2.0 + 25.0
            node.right_ext = node.box_w / 2.0 + comm_w + 25.0
            node.height = node.box_h

        elif isinstance(node, FuncNode):
            node.header_node = BlockNode(
                kind="func_header",
                text=node.signature,
                comment=node.comment
            )
            self._measure_node(node.header_node, allow_center_shift=False)
            # На верхнем уровне тела функции выход из цикла смещает центральную ось программы
            body_l, body_r, body_h = self._measure_sequence(node.body, allow_center_shift=True)
            node.left_ext = max(node.header_node.left_ext + 20.0, body_l)
            node.right_ext = max(node.header_node.right_ext, body_r + 25.0)
            node.height = node.header_node.height + (self.V_GAP + body_h if node.body else 0.0) + 20.0

        elif isinstance(node, IfNode):
            tw, th, _ = self._measure_text(node.condition)
            node.diamond_w = 2.0 * (tw + self.PAD_X * 1.4)
            node.diamond_h = max(2.0 * (th + self.PAD_Y * 1.3), 56.0)

            node.top_pad = 0.0
            if node.comment:
                _, comm_h, _ = self._measure_text(node.comment)
                half_dh = node.diamond_h / 2.0
                needed_above_center = 28.0 + comm_h
                if needed_above_center > half_dh:
                    node.top_pad = needed_above_center - half_dh + 6.0

            tl, tr, th_branch = self._measure_sequence(node.true_branch, allow_center_shift=False)
            fl, fr, fh_branch = self._measure_sequence(node.false_branch, allow_center_shift=False)

            half_dw = node.diamond_w / 2.0
            min_shoulder = 48.0

            node.offset_l = max(half_dw + min_shoulder, tr + self.H_GAP / 2.0)
            node.offset_r = max(half_dw + min_shoulder, fl + self.H_GAP / 2.0)

            node.branch_h = max(th_branch, fh_branch, 30.0)
            node.height = node.top_pad + node.diamond_h + self.V_GAP + node.branch_h + self.V_GAP
            node.left_ext = node.offset_l + max(tl, 30.0)
            comm_right_reach = 0.35 * half_dw + 28.0 + comm_w if node.comment else 0.0
            node.right_ext = max(node.offset_r + max(fr, 30.0), comm_right_reach)

        elif isinstance(node, LoopNode):
            tw, th, _ = self._measure_text(node.header)
            if node.loop_kind == "for":
                # Шестиугольник: плоская центральная часть = tw + 2*PAD_X, плюс треугольные края hex_tip_w
                node.shape_h = max(th + 2 * self.PAD_Y, 46.0)
                node.hex_tip_w = max(node.shape_h * 0.55, 24.0)
                node.shape_w = tw + 2 * self.PAD_X + 2 * node.hex_tip_w
            else:
                # Ромб для while
                node.shape_w = 2.0 * (tw + self.PAD_X * 1.4)
                node.shape_h = max(2.0 * (th + self.PAD_Y * 1.3), 56.0)
                node.hex_tip_w = node.shape_w / 2.0

            node.top_pad = 0.0
            if node.comment:
                _, comm_h, _ = self._measure_text(node.comment)
                half_sh = node.shape_h / 2.0
                needed_above_center = 28.0 + comm_h
                if needed_above_center > half_sh:
                    node.top_pad = needed_above_center - half_sh + 8.0

            # Внутри тела цикла все вложенные циклы остаются на одной оси (allow_center_shift=False)
            bl, br, bh = self._measure_sequence(node.body, allow_center_shift=False)
            node.body_h = max(bh, 30.0)
            half_sw = node.shape_w / 2.0

            # Линия возврата слева огибает все вложенные циклы и блоки тела без пересечений
            node.left_back_offset = max(half_sw + 40.0, bl + 28.0)
            # Линия выхода справа огибает все тело цикла
            node.right_exit_offset = max(half_sw + 54.0, br + 38.0)

            node.left_ext = node.left_back_offset + 25.0
            comm_right_reach = half_sw + 24.0 + comm_w if node.comment else 0.0
            node.right_ext = max(node.right_exit_offset + 30.0, comm_right_reach)

            bottom_tail = 18.0 if allow_center_shift else 48.0
            node.height = node.top_pad + node.shape_h + self.V_GAP + node.body_h + bottom_tail

        elif isinstance(node, SwitchNode):
            node.header_block = BlockNode(kind="rect", text=node.header_text, comment=node.comment)
            self._measure_node(node.header_block)

            max_dw = 110.0
            for c in node.cases:
                tw, th, _ = self._measure_text(c.label)
                c.diamond_w = max(2.0 * (tw + self.PAD_X * 1.2), 110.0)
                c.diamond_h = max(2.0 * (th + self.PAD_Y * 1.2), 54.0)
                max_dw = max(max_dw, c.diamond_w)

            node.max_diamond_w = max_dw
            max_row_right = node.header_block.right_ext
            total_cases_h = 0.0

            for idx, c in enumerate(node.cases):
                c.diamond_w = max_dw
                cur_x = max_dw / 2.0
                max_box_h = c.diamond_h
                max_comm_top = 0.0
                row_rightmost = cur_x + self.SWITCH_FALL_SHOULDER + 25.0

                if c.comment:
                    cw, ch, _ = self._measure_text(c.comment)
                    max_comm_top = max(max_comm_top, ch + 18.0)
                    row_rightmost = max(row_rightmost, cur_x + 16.0 + cw + 20.0)

                for st_idx, st in enumerate(c.statements):
                    self._measure_node(st)
                    gap = self.SWITCH_TRUE_GAP if st_idx == 0 else self.SWITCH_STMT_GAP
                    st_left = cur_x + gap
                    st_right = st_left + st.box_w
                    row_rightmost = max(row_rightmost, st_right)
                    max_box_h = max(max_box_h, st.box_h)

                    if st.comment:
                        cw, ch, _ = self._measure_text(st.comment)
                        max_comm_top = max(max_comm_top, ch + 22.0)
                        row_rightmost = max(row_rightmost, st_left + cw + 20.0)

                    cur_x = st_right

                c.top_pad = max_comm_top
                c.row_h = max_box_h + c.top_pad
                c.row_w = row_rightmost
                max_row_right = max(max_row_right, row_rightmost + 40.0)
                total_cases_h += c.row_h
                if idx < len(node.cases) - 1:
                    total_cases_h += self.SWITCH_CASE_V_GAP

            node.collector_x_offset = max_row_right
            node.left_ext = max(node.header_block.left_ext + 20.0, max_dw / 2.0 + 35.0)
            node.right_ext = node.collector_x_offset + 40.0
            node.height = (
                node.header_block.height
                + self.V_GAP
                + total_cases_h
                + self.SWITCH_BOTTOM_GAP
                + 20.0
            )

    def _measure_sequence(
        self, nodes: List[Node], allow_center_shift: bool = False
    ) -> Tuple[float, float, float]:
        if not nodes:
            return 25.0, 25.0, 0.0
        max_l = 25.0
        max_r = 25.0
        total_h = 0.0
        curr_shift = 0.0

        for idx, n in enumerate(nodes):
            self._measure_node(n, allow_center_shift=allow_center_shift)
            max_l = max(max_l, n.left_ext - curr_shift)
            max_r = max(max_r, curr_shift + n.right_ext)
            total_h += n.height
            if idx < len(nodes) - 1:
                total_h += self.V_GAP
            if isinstance(n, LoopNode) and allow_center_shift:
                curr_shift += n.right_exit_offset

        return max_l, max_r, total_h

    def _draw_text_with_slashed_zeros(
        self,
        cx: float,
        cy: float,
        text: str,
        anchor: str = "middle",
        color: str = "#111111",
        bg_mask: bool = False
    ):
        _, total_h, lines = self._measure_text(text)
        if bg_mask and text:
            actual_w = max(len(line) for line in lines) * self.CHAR_W + 8.0
            if anchor == "middle":
                bx = cx - actual_w / 2.0
            elif anchor == "start":
                bx = cx - 4.0
            else:
                bx = cx - actual_w + 4.0
            by = cy - total_h / 2.0 - 1.0
            self.svg_elements.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{actual_w:.1f}" '
                f'height="{total_h + 2.0:.1f}" fill="#ffffff" />'
            )

        start_y = cy - total_h / 2.0 + self.LINE_H / 2.0

        for row_idx, line in enumerate(lines):
            line_y = start_y + row_idx * self.LINE_H
            text_baseline_y = line_y + self.FONT_SIZE * 0.35
            escaped = html.escape(line)

            self.svg_elements.append(
                f'<text x="{cx:.1f}" y="{text_baseline_y:.1f}" '
                f'text-anchor="{anchor}" font-family="Courier New, Liberation Mono, monospace" '
                f'font-size="{self.FONT_SIZE}" fill="{color}" xml:space="preserve">{escaped}</text>'
            )

            line_w = len(line) * self.CHAR_W
            if anchor == "middle":
                line_start_x = cx - line_w / 2.0
            elif anchor == "start":
                line_start_x = cx
            else:
                line_start_x = cx - line_w

            for char_idx, ch in enumerate(line):
                if ch == "0":
                    zero_cx = line_start_x + (char_idx + 0.5) * self.CHAR_W
                    zero_cy = line_y + 0.5
                    dx = self.CHAR_W * 0.36
                    dy = self.FONT_SIZE * 0.38
                    self.svg_elements.append(
                        f'<line x1="{zero_cx + dx:.2f}" y1="{zero_cy - dy:.2f}" '
                        f'x2="{zero_cx - dx:.2f}" y2="{zero_cy + dy:.2f}" '
                        f'stroke="{color}" stroke-width="1.5" stroke-linecap="round" />'
                    )

    def _draw_arrow(self, x1: float, y1: float, x2: float, y2: float):
        self.svg_elements.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#111111" stroke-width="1.8" marker-end="url(#arrow)" />'
        )

    def _draw_line(self, x1: float, y1: float, x2: float, y2: float, dashed: bool = False):
        dash = ' stroke-dasharray="6,4"' if dashed else ""
        self.svg_elements.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#111111" stroke-width="1.8"{dash} />'
        )

    def _draw_brace_symbol(self, x: float, y: float, symbol: str):
        self.svg_elements.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-family="Courier New, Liberation Mono, monospace" '
            f'font-size="20" font-weight="bold" fill="#111111">{symbol}</text>'
        )

    def _draw_comment(self, right_edge_x: float, cy: float, comment: str):
        if not comment:
            return
        comm_x = right_edge_x + 18.0
        self._draw_line(right_edge_x + 2.0, cy, comm_x - 4.0, cy, dashed=True)
        self._draw_text_with_slashed_zeros(
            comm_x, cy, comment, anchor="start", color="#333333", bg_mask=True
        )

    def _draw_diamond_comment(
        self, cx: float, d_top: float, d_cy: float, dw: float, comment: str, is_hex: bool = False, tip_w: float = 0.0
    ):
        if not comment:
            return
        _, comm_h, _ = self._measure_text(comment)
        comm_cy = d_cy - 26.0 - comm_h / 2.0
        if is_hex:
            edge_x = cx + dw / 2.0 - tip_w * 0.5
            edge_y = (d_top + d_cy) / 2.0
        else:
            t = 0.35
            edge_x = cx + t * (dw / 2.0)
            edge_y = d_top + t * (d_cy - d_top)
        comm_x = edge_x + 26.0

        self._draw_line(edge_x + 1.0, edge_y, comm_x - 5.0, comm_cy, dashed=True)
        self._draw_text_with_slashed_zeros(
            comm_x, comm_cy, comment, anchor="start", color="#333333", bg_mask=True
        )

    def _draw_top_comment(self, box_left_x: float, box_cx: float, box_top_y: float, comment: str):
        if not comment:
            return
        _, ch, _ = self._measure_text(comment)
        comm_cy = box_top_y - 12.0 - ch / 2.0
        self._draw_line(box_cx, box_top_y - 1.0, box_cx, box_top_y - 10.0, dashed=True)
        self._draw_text_with_slashed_zeros(
            box_left_x, comm_cy, comment, anchor="start", color="#333333", bg_mask=True
        )

    def _render_block(
        self, node: BlockNode, cx: float, top_y: float, draw_side_comment: bool = True
    ) -> float:
        w, h = node.box_w, node.box_h
        cy = top_y + h / 2.0
        left_x = cx - w / 2.0
        right_x = cx + w / 2.0
        bot_y = top_y + h

        if node.kind == "oval":
            rx = h / 2.0
            self.svg_elements.append(
                f'<rect x="{left_x:.1f}" y="{top_y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                f'rx="{rx:.1f}" ry="{rx:.1f}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
            )
        elif node.kind == "io":
            s = self.IO_SLANT
            pts = (
                f"{left_x + s:.1f},{top_y:.1f} "
                f"{right_x + s:.1f},{top_y:.1f} "
                f"{right_x - s:.1f},{bot_y:.1f} "
                f"{left_x - s:.1f},{bot_y:.1f}"
            )
            self.svg_elements.append(
                f'<polygon points="{pts}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
            )
        elif node.kind == "func_header":
            self.svg_elements.append(
                f'<rect x="{left_x:.1f}" y="{top_y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                f'fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
            )
            s = self.FUNC_STRIPE
            self._draw_line(left_x + s, top_y, left_x + s, bot_y)
            self._draw_line(right_x - s, top_y, right_x - s, bot_y)
        else:
            self.svg_elements.append(
                f'<rect x="{left_x:.1f}" y="{top_y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                f'fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
            )

        self._draw_text_with_slashed_zeros(cx, cy, node.text, anchor="middle")
        if draw_side_comment:
            self._draw_comment(right_x, cy, node.comment)
        return bot_y

    def _render_sequence(
        self,
        nodes: List[Node],
        cx: float,
        start_y: float,
        show_braces_if_multi: bool = False,
        allow_center_shift: bool = False
    ) -> Tuple[float, float]:
        curr_y = start_y
        curr_cx = cx

        if show_braces_if_multi and len(nodes) > 1:
            self._draw_brace_symbol(curr_cx - 16.0, start_y - 10.0, "{")

        for idx, n in enumerate(nodes):
            bot_y, curr_cx = self._render_node(
                n, curr_cx, curr_y, allow_center_shift=allow_center_shift
            )
            if idx < len(nodes) - 1:
                next_y = bot_y + self.V_GAP
                self._draw_arrow(curr_cx, bot_y, curr_cx, next_y)
                curr_y = next_y
            else:
                curr_y = bot_y

        if show_braces_if_multi and len(nodes) > 1:
            self._draw_brace_symbol(curr_cx + 16.0, curr_y + 18.0, "}")

        return curr_y, curr_cx

    def _render_node(
        self, node: Node, cx: float, top_y: float, allow_center_shift: bool = False
    ) -> Tuple[float, float]:
        if isinstance(node, BlockNode):
            bot_y = self._render_block(node, cx, top_y)
            return bot_y, cx

        if isinstance(node, FuncNode):
            hdr_bot = self._render_block(node.header_node, cx, top_y)
            if not node.body:
                return hdr_bot, cx

            body_start_y = hdr_bot + self.V_GAP
            self._draw_arrow(cx, hdr_bot, cx, body_start_y)
            self._draw_brace_symbol(cx - 16.0, hdr_bot + self.V_GAP * 0.55, "{")

            body_bot, end_cx = self._render_sequence(
                node.body, cx, body_start_y, show_braces_if_multi=False, allow_center_shift=True
            )
            self._draw_brace_symbol(end_cx + 18.0, body_bot + 18.0, "}")
            return body_bot + 20.0, end_cx

        if isinstance(node, IfNode):
            d_top = top_y + node.top_pad
            if node.top_pad > 0:
                self._draw_line(cx, top_y, cx, d_top)

            dw, dh = node.diamond_w, node.diamond_h
            d_cy = d_top + dh / 2.0
            d_bot = d_top + dh
            left_vx = cx - dw / 2.0
            right_vx = cx + dw / 2.0

            pts = (
                f"{cx:.1f},{d_top:.1f} "
                f"{right_vx:.1f},{d_cy:.1f} "
                f"{cx:.1f},{d_bot:.1f} "
                f"{left_vx:.1f},{d_cy:.1f}"
            )
            self.svg_elements.append(
                f'<polygon points="{pts}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
            )
            self._draw_text_with_slashed_zeros(cx, d_cy, node.condition, anchor="middle")
            self._draw_diamond_comment(cx, d_top, d_cy, dw, node.comment)

            lx = cx - node.offset_l
            rx = cx + node.offset_r
            branch_top_y = d_bot + self.V_GAP
            merge_y = branch_top_y + node.branch_h + self.V_GAP

            self._draw_line(left_vx, d_cy, lx, d_cy)
            self._draw_text_with_slashed_zeros(
                (left_vx + lx) / 2.0, d_cy - 11.0, "1", bg_mask=True
            )

            self._draw_line(right_vx, d_cy, rx, d_cy)
            self._draw_text_with_slashed_zeros(
                (right_vx + rx) / 2.0, d_cy - 11.0, "0", bg_mask=True
            )

            if node.true_branch:
                self._draw_arrow(lx, d_cy, lx, branch_top_y)
                t_bot, _ = self._render_sequence(
                    node.true_branch, lx, branch_top_y, show_braces_if_multi=True, allow_center_shift=False
                )
                self._draw_line(lx, t_bot, lx, merge_y)
            else:
                self._draw_line(lx, d_cy, lx, merge_y)

            if node.false_branch:
                self._draw_arrow(rx, d_cy, rx, branch_top_y)
                f_bot, _ = self._render_sequence(
                    node.false_branch, rx, branch_top_y, show_braces_if_multi=True, allow_center_shift=False
                )
                self._draw_line(rx, f_bot, rx, merge_y)
            else:
                self._draw_line(rx, d_cy, rx, merge_y)

            self._draw_arrow(lx, merge_y, cx - 2.0, merge_y)
            self._draw_arrow(rx, merge_y, cx + 2.0, merge_y)
            self.svg_elements.append(
                f'<circle cx="{cx:.1f}" cy="{merge_y:.1f}" r="2.2" fill="#111111" />'
            )
            return merge_y, cx

        if isinstance(node, LoopNode):
            d_top = top_y + node.top_pad
            if node.top_pad > 0:
                self._draw_line(cx, top_y, cx, d_top)

            sw, sh = node.shape_w, node.shape_h
            d_cy = d_top + sh / 2.0
            d_bot = d_top + sh
            left_vx = cx - sw / 2.0
            right_vx = cx + sw / 2.0

            if node.loop_kind == "for":
                # Шестиугольник для цикла for
                tw_tip = node.hex_tip_w
                pts = (
                    f"{left_vx:.1f},{d_cy:.1f} "
                    f"{left_vx + tw_tip:.1f},{d_top:.1f} "
                    f"{right_vx - tw_tip:.1f},{d_top:.1f} "
                    f"{right_vx:.1f},{d_cy:.1f} "
                    f"{right_vx - tw_tip:.1f},{d_bot:.1f} "
                    f"{left_vx + tw_tip:.1f},{d_bot:.1f}"
                )
                self.svg_elements.append(
                    f'<polygon points="{pts}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
                )
                self._draw_text_with_slashed_zeros(cx, d_cy, node.header, anchor="middle")
                self._draw_diamond_comment(
                    cx, d_top, d_cy, sw, node.comment, is_hex=True, tip_w=tw_tip
                )
            else:
                # Ромб для цикла while
                pts = (
                    f"{cx:.1f},{d_top:.1f} "
                    f"{right_vx:.1f},{d_cy:.1f} "
                    f"{cx:.1f},{d_bot:.1f} "
                    f"{left_vx:.1f},{d_cy:.1f}"
                )
                self.svg_elements.append(
                    f'<polygon points="{pts}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
                )
                self._draw_text_with_slashed_zeros(cx, d_cy, node.header, anchor="middle")
                self._draw_diamond_comment(cx, d_top, d_cy, sw, node.comment, is_hex=False)

            # Вниз идет тело цикла (ветка 1)
            body_start_y = d_bot + self.V_GAP
            self._draw_arrow(cx, d_bot, cx, body_start_y)
            self._draw_text_with_slashed_zeros(
                cx + 12.0, d_bot + self.V_GAP * 0.42, "1", bg_mask=True
            )

            if node.body:
                body_bot, _ = self._render_sequence(
                    node.body, cx, body_start_y, show_braces_if_multi=True, allow_center_shift=False
                )
            else:
                body_bot = body_start_y + 20.0

            # Возврат в левую вершину фигуры ровно тремя поворотами:
            # 1) вниз до back_bottom_y -> поворот влево
            # 2) влево до back_x -> поворот вверх
            # 3) вверх до d_cy -> поворот вправо в левый угол (left_vx, d_cy)
            back_bottom_y = body_bot + 24.0
            back_x = cx - node.left_back_offset
            self._draw_line(cx, body_bot, cx, back_bottom_y)
            self._draw_line(cx, back_bottom_y, back_x, back_bottom_y)
            self._draw_line(back_x, back_bottom_y, back_x, d_cy)
            self._draw_arrow(back_x, d_cy, left_vx, d_cy)

            # Выход из правой части цикла (ветка 0)
            rx = cx + node.right_exit_offset
            self._draw_line(right_vx, d_cy, rx, d_cy)
            self._draw_text_with_slashed_zeros(
                right_vx + 24.0, d_cy - 11.0, "0", bg_mask=True
            )

            if allow_center_shift:
                # Правая ветка становится новым центром программы
                out_y = back_bottom_y + 10.0
                self._draw_line(rx, d_cy, rx, out_y)
                return out_y, rx
            else:
                # Внутри другого цикла или ветки: возвращаем линию на текущую ось cx,
                # чтобы последовательные внутренние циклы стояли на одной линии
                merge_y = back_bottom_y + 24.0
                self._draw_line(rx, d_cy, rx, merge_y)
                self._draw_arrow(rx, merge_y, cx, merge_y)
                self.svg_elements.append(
                    f'<circle cx="{cx:.1f}" cy="{merge_y:.1f}" r="2.2" fill="#111111" />'
                )
                return merge_y, cx

        if isinstance(node, SwitchNode):
            hdr_bot = self._render_block(node.header_block, cx, top_y)
            if not node.cases:
                return hdr_bot, cx

            curr_y = hdr_bot + self.V_GAP
            first_c = node.cases[0]
            first_box_area_h = first_c.row_h - first_c.top_pad
            first_d_top = curr_y + first_c.top_pad + (first_box_area_h - first_c.diamond_h) / 2.0

            self._draw_arrow(cx, hdr_bot, cx, first_d_top)
            self._draw_brace_symbol(cx - 16.0, hdr_bot + self.V_GAP * 0.55, "{")

            collector_x = cx + node.collector_x_offset
            first_collector_cy = None

            # Предварительно рассчитываем координаты Y центров всех веток case
            row_top_list: List[float] = []
            row_cy_list: List[float] = []
            temp_y = curr_y
            for c in node.cases:
                row_top_list.append(temp_y)
                box_area_h = c.row_h - c.top_pad
                row_cy_list.append(temp_y + c.top_pad + box_area_h / 2.0)
                temp_y += c.row_h + self.SWITCH_CASE_V_GAP

            for idx, c in enumerate(node.cases):
                dw, dh = c.diamond_w, c.diamond_h
                row_cy = row_cy_list[idx]

                d_top = row_cy - dh / 2.0
                d_bot = row_cy + dh / 2.0
                left_vx = cx - dw / 2.0
                right_vx = cx + dw / 2.0
                fall_x = right_vx + self.SWITCH_FALL_SHOULDER

                pts = (
                    f"{cx:.1f},{d_top:.1f} "
                    f"{right_vx:.1f},{row_cy:.1f} "
                    f"{cx:.1f},{d_bot:.1f} "
                    f"{left_vx:.1f},{row_cy:.1f}"
                )
                self.svg_elements.append(
                    f'<polygon points="{pts}" fill="#ffffff" stroke="#111111" stroke-width="1.8" />'
                )
                self._draw_text_with_slashed_zeros(cx, row_cy, c.label, anchor="middle")

                if c.comment:
                    self._draw_top_comment(right_vx + 12.0, right_vx + 20.0, row_cy, c.comment)

                # Отрисовка ветки True с учетом провалов (fallthrough)
                if c.falls_through and not c.statements:
                    # Пустой провал: из True с плечиком вниз на линию выполнения следующего case перед командами
                    next_row_cy = row_cy_list[idx + 1]
                    self._draw_line(right_vx, row_cy, fall_x, row_cy)
                    self._draw_text_with_slashed_zeros(
                        right_vx + 25.0, row_cy - 11.0, "True", anchor="middle", bg_mask=True
                    )
                    self._draw_arrow(fall_x, row_cy, fall_x, next_row_cy)
                    self.svg_elements.append(
                        f'<circle cx="{fall_x:.1f}" cy="{next_row_cy:.1f}" r="2.2" fill="#111111" />'
                    )
                else:
                    cur_x = right_vx
                    for st_idx, st in enumerate(c.statements):
                        gap = self.SWITCH_TRUE_GAP if st_idx == 0 else self.SWITCH_STMT_GAP
                        next_left_x = cur_x + gap
                        self._draw_arrow(cur_x, row_cy, next_left_x, row_cy)
                        if st_idx == 0:
                            self._draw_text_with_slashed_zeros(
                                right_vx + 25.0, row_cy - 11.0, "True", anchor="middle", bg_mask=True
                            )
                        st_cx = next_left_x + st.box_w / 2.0
                        st_top = row_cy - st.box_h / 2.0
                        self._render_block(st, st_cx, st_top, draw_side_comment=False)
                        if st.comment:
                            self._draw_top_comment(next_left_x, st_cx, st_top, st.comment)
                        cur_x = next_left_x + st.box_w

                    if c.falls_through:
                        # Провал после выполнения команд без break: уходит вниз на линию следующего case перед его командами
                        next_row_cy = row_cy_list[idx + 1]
                        drop_x = cur_x + 20.0
                        mid_y = (d_bot + (row_cy_list[idx + 1] - node.cases[idx + 1].diamond_h / 2.0)) / 2.0
                        self._draw_line(cur_x, row_cy, drop_x, row_cy)
                        self._draw_line(drop_x, row_cy, drop_x, mid_y)
                        self._draw_line(drop_x, mid_y, fall_x, mid_y)
                        self._draw_arrow(fall_x, mid_y, fall_x, next_row_cy)
                        self.svg_elements.append(
                            f'<circle cx="{fall_x:.1f}" cy="{next_row_cy:.1f}" r="2.2" fill="#111111" />'
                        )
                    else:
                        if first_collector_cy is None:
                            first_collector_cy = row_cy
                        self._draw_line(cur_x, row_cy, collector_x, row_cy)

                # Вертикальный переход False вниз к следующему ромбу case
                if idx < len(node.cases) - 1:
                    next_c = node.cases[idx + 1]
                    next_d_top = row_cy_list[idx + 1] - next_c.diamond_h / 2.0
                    self._draw_arrow(cx, d_bot, cx, next_d_top)
                    false_y = d_bot + (next_d_top - d_bot) * 0.44
                    self._draw_text_with_slashed_zeros(
                        cx, false_y, "False", anchor="middle", bg_mask=True
                    )
                else:
                    merge_y = d_bot + self.SWITCH_BOTTOM_GAP
                    self._draw_line(cx, d_bot, cx, merge_y)
                    false_y = d_bot + self.SWITCH_BOTTOM_GAP * 0.38
                    self._draw_text_with_slashed_zeros(
                        cx, false_y, "False", anchor="middle", bg_mask=True
                    )
                    if first_collector_cy is not None:
                        self._draw_line(collector_x, first_collector_cy, collector_x, merge_y)
                        self._draw_arrow(collector_x, merge_y, cx + 2.0, merge_y)
                        self.svg_elements.append(
                            f'<circle cx="{cx:.1f}" cy="{merge_y:.1f}" r="2.2" fill="#111111" />'
                        )
                    self._draw_brace_symbol(cx + 18.0, merge_y + 18.0, "}")
                    return merge_y, cx

        return top_y, cx

    def render(self) -> str:
        start_node = BlockNode(kind="oval", text="начало")
        self._measure_node(start_node)

        seq_l, seq_r, _ = self._measure_sequence(
            self.ast.globals_before, allow_center_shift=True
        )

        preamble_text = "\n".join(self.ast.preamble)
        pre_w, pre_h, _ = self._measure_text(preamble_text) if self.ast.preamble else (0.0, 0.0, [])
        first_arrow_len = max(self.V_GAP, pre_h + 24.0) if self.ast.preamble else self.V_GAP

        center_x = max(seq_l, start_node.left_ext) + 60.0
        right_bound = center_x + max(seq_r, start_node.right_ext + pre_w + 110.0) + 60.0
        total_w = max(right_bound, 500.0)

        curr_y = 40.0
        start_bot = self._render_block(start_node, center_x, curr_y)

        first_stmt_y = start_bot + first_arrow_len
        self._draw_arrow(center_x, start_bot, center_x, first_stmt_y)

        if self.ast.preamble:
            mid_arrow_y = start_bot + first_arrow_len / 2.0
            bracket_x = center_x + 65.0
            self._draw_line(center_x, mid_arrow_y, bracket_x, mid_arrow_y, dashed=True)

            b_top = mid_arrow_y - pre_h / 2.0 - 6.0
            b_bot = mid_arrow_y + pre_h / 2.0 + 6.0
            self._draw_line(bracket_x, b_top, bracket_x, b_bot)
            self._draw_line(bracket_x, b_top, bracket_x + 10.0, b_top)
            self._draw_line(bracket_x, b_bot, bracket_x + 10.0, b_bot)

            self._draw_text_with_slashed_zeros(
                bracket_x + 16.0, mid_arrow_y, preamble_text, anchor="start"
            )

        final_y, _ = self._render_sequence(
            self.ast.globals_before,
            center_x,
            first_stmt_y,
            show_braces_if_multi=False,
            allow_center_shift=True
        )
        total_h = final_y + 60.0

        svg_header = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{total_w:.0f}" height="{total_h:.0f}" viewBox="0 0 {total_w:.0f} {total_h:.0f}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#111111" />
    </marker>
  </defs>
  <rect width="100%" height="100%" fill="#ffffff" />
"""
        return svg_header + "\n  ".join(self.svg_elements) + "\n</svg>\n"


def main():
    parser = argparse.ArgumentParser(description="Генератор блок-схем C++ -> SVG")
    parser.add_argument("input", help="Путь к исходному C++ файлу (.cpp)")
    parser.add_argument("-o", "--output", default="flowchart.svg", help="Выходной SVG файл")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        cpp_code = f.read()

    ast = CppFlowParser(cpp_code).parse()
    svg_content = FlowchartSVGRenderer(ast).render()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Готово! Блок-схема сохранена в: {args.output}")


if __name__ == "__main__":
    main()