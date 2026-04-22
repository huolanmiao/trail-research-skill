"""Generate 活动备案表 (Activity Registration Form) as .docx file.

Only outputs the main content sections 一 through 五 — no header form,
approval block, or footer notes. Content-focused, format-flexible.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_model import TrailResearchData
from docx_utils import (
    create_document, add_heading_styled, add_paragraph_styled,
    add_table_with_data, save_document
)


def generate_registration_form(data: TrailResearchData, output_path: str) -> str:
    doc = create_document()

    # ============================================================
    # Section 1: 路线简介
    # ============================================================
    add_heading_styled(doc, "一、路线简介", level=1)

    route_summary = (
        f"全程路线清晰，全程约{data.route.total_distance_km}km，"
        f"爬升约{data.route.total_elevation_gain_m}m，"
        f"以{data.route.surface_summary or '土路、防火道为主'}。"
    )
    add_paragraph_styled(doc, route_summary)

    if data.route.segments:
        for seg in data.route.segments:
            seg_text = f"{seg.name}：约{seg.distance_km}km，爬升{seg.elevation_gain_m}m"
            if seg.surface_types:
                seg_text += f"，路况为{'、'.join(seg.surface_types)}"
            if seg.description:
                seg_text += f"。{seg.description}"
            add_paragraph_styled(doc, seg_text)

    score = data.calc_difficulty_score()
    grade = data.route.difficulty_grade or data.calc_difficulty_grade()
    add_paragraph_styled(doc,
        f"路线强度 = {score:.1f}，属于{grade}强度。"
        f"{data.route.suitability or '适合有一定徒步经验的同学参加。'}")

    if data.route.gps_track_links:
        add_paragraph_styled(doc, "参考轨迹：")
        for link in data.route.gps_track_links:
            add_paragraph_styled(doc, f"  - {link}")

    # ============================================================
    # Section 2: 领队介绍
    # ============================================================
    add_heading_styled(doc, "二、领队介绍", level=1)

    leader_count = len(data.organization.leaders)
    ratio = data.organization.leader_ratio or f"1:{data.organization.max_participants // max(leader_count, 1)}"
    main_leaders = sum(1 for l in data.organization.leaders if l.role == "主领队")

    add_paragraph_styled(doc,
        f"本次活动预计总人数{data.organization.max_participants}人，"
        f"领队{leader_count}人，领队比例{ratio}，"
        f"具有担任主领队资格的领队{main_leaders}人。以下为领队介绍：")

    for leader in data.organization.leaders:
        add_paragraph_styled(doc, f"{leader.name}：{leader.bio}")

    # ============================================================
    # Section 3: 线路风险
    # ============================================================
    add_heading_styled(doc, "三、线路风险", level=1)

    risk_summary = "本次徒步活动主要风险包括："
    high_risks = [r for r in data.risks if r.risk_level in ("风险容易发生", "危险", "很危险", "极度危险")]
    if high_risks:
        risk_summary += "、".join(f"{r.risk_cause}（{r.risk_level}）" for r in high_risks)
    else:
        risk_summary += "体能耗竭、崴脚、树枝划伤等常规户外风险，整体风险可控。"
    add_paragraph_styled(doc, risk_summary)

    risk_headers = ["序号", "风险原因", "风险级别", "应对要求"]
    risk_rows = []
    for r in data.risks:
        mit = r.mitigation
        if len(mit) > 60:
            mit = mit[:60] + "……"
        risk_rows.append([str(r.seq), r.risk_cause, r.risk_level, mit])
    add_table_with_data(doc, risk_headers, risk_rows)

    # ============================================================
    # Section 4: 行进节奏
    # ============================================================
    add_heading_styled(doc, "四、行进节奏", level=1)

    if data.organization.schedule:
        sched_headers = ["时间", "事项"]
        sched_rows = [[s.time, s.activity] for s in data.organization.schedule]
        add_table_with_data(doc, sched_headers, sched_rows, col_widths=[5, 11])

    if data.route.segments:
        add_paragraph_styled(doc, "分段行进计划：", bold=True)
        seg_headers = ["路段", "里程(km)", "爬升(m)", "预计用时", "路况"]
        seg_rows = []
        for seg in data.route.segments:
            surface_str = "、".join(seg.surface_types) if seg.surface_types else ""
            speed = 2.5 if seg.elevation_gain_m > 200 else 4.0
            hours = seg.distance_km / speed
            seg_rows.append([
                seg.name,
                str(seg.distance_km),
                str(seg.elevation_gain_m),
                f"约{hours:.1f}h",
                surface_str,
            ])
        add_table_with_data(doc, seg_headers, seg_rows)

    # ============================================================
    # Section 5: 装备与注意事项
    # ============================================================
    add_heading_styled(doc, "五、装备与注意事项", level=1)

    if data.gear:
        category_order = ["必备", "强烈推荐", "可选", "按季节"]
        gear_by_category = {cat: [] for cat in category_order}
        for g in data.gear:
            cat = g.category if g.category in gear_by_category else "其他"
            if cat not in gear_by_category:
                gear_by_category[cat] = []
            gear_by_category[cat].append(g)

        idx = 1
        for cat in category_order:
            items = gear_by_category.get(cat, [])
            if not items:
                continue
            item_texts = []
            for g in items:
                if g.notes:
                    item_texts.append(f"{g.name}（{g.notes}）")
                else:
                    item_texts.append(g.name)
            add_paragraph_styled(doc, f"{idx}. {cat}：{'、'.join(item_texts)}。")
            idx += 1

        for cat, items in gear_by_category.items():
            if cat in category_order or not items:
                continue
            item_texts = []
            for g in items:
                if g.notes:
                    item_texts.append(f"{g.name}（{g.notes}）")
                else:
                    item_texts.append(g.name)
            add_paragraph_styled(doc, f"{idx}. {cat}：{'、'.join(item_texts)}。")
            idx += 1
    else:
        add_paragraph_styled(doc, "1. 衣物：三层穿衣法，内层至少两件可更换的速干衣，中间层透气的软壳和用于保暖的抓绒（怕冷可备薄羽绒），外层冲锋衣和雨衣。下半身至少一层中间层，外层建议冲锋裤或防泼水软壳裤。")
        add_paragraph_styled(doc, "2. 鞋袜：推荐穿越野跑鞋、徒步鞋等有防滑能力的鞋子，不穿新鞋、板鞋，禁止高跟鞋、拖鞋。袜子推荐中筒或高筒徒步袜。")
        add_paragraph_styled(doc, "3. 饮食：早餐必须吃；午餐自备，建议不要自热火锅。水与功能饮料合计建议携带1.5-2.5L。")
        add_paragraph_styled(doc, "4. 必备：充电宝、身份证/护照、非一次性雨衣、纸巾、少量现金、垃圾袋。")
        add_paragraph_styled(doc, "5. 强烈推荐：手台、登山杖、护膝。")

    if data.registration_notes:
        add_paragraph_styled(doc, f"其他：{data.registration_notes}")

    save_document(doc, output_path)
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_registration_form.py <input_json> <output_path>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_path = sys.argv[2]

    try:
        data = TrailResearchData.from_json(input_json)
    except Exception as e:
        print(f"Error loading data from {input_json}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = generate_registration_form(data, output_path)
        print(f"Registration form saved to: {result}")
    except Exception as e:
        print(f"Error generating registration form: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
