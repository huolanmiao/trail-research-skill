"""Generate 领队计划 (Leader Plan) as .docx file."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_model import TrailResearchData
from docx_utils import (
    create_document, add_heading_styled, add_paragraph_styled,
    add_table_with_data, add_field_table, add_bullet_list,
    save_document
)


def generate_leader_plan(data: TrailResearchData, output_path: str) -> str:
    doc = create_document()

    # ============================================================
    # Section 1: 活动介绍
    # ============================================================
    add_heading_styled(doc, "一、活动介绍", level=1)

    activity_name = data.activity.name or data.route.name
    intro_para = (
        f"本次徒步活动目的地为{data.route.location}的{data.route.name}，"
        f"全程约{data.route.total_distance_km}km，累计爬升约{data.route.total_elevation_gain_m}m，"
        f"属于{data.route.difficulty_grade}强度路线。"
    )
    add_paragraph_styled(doc, intro_para)

    if data.route.history_culture:
        add_paragraph_styled(doc, data.route.history_culture)

    if data.route.scenery_highlights:
        add_paragraph_styled(doc, data.route.scenery_highlights)

    add_paragraph_styled(doc, "（配图位置：请插入路线风景照片，标注来源）")
    add_paragraph_styled(doc, "图源自网络，侵删。受天气影响，不一定能看见同款风景。", font_size=9)

    # ============================================================
    # Section 2: 路线信息
    # ============================================================
    add_heading_styled(doc, "二、路线信息", level=1)

    # 2.1 徒步路线
    add_heading_styled(doc, "1. 徒步路线", level=2)
    route_desc = (
        f"徒步路线：{data.route.name}\n"
        f"路线类型：{data.route.route_type or '环线/穿越'}\n"
        f"总里程：{data.route.total_distance_km} km\n"
        f"累计爬升：{data.route.total_elevation_gain_m} m\n"
        f"累计下降：{data.route.total_elevation_loss_m if data.route.total_elevation_loss_m > 0 else data.route.total_elevation_gain_m} m\n"
        f"信号覆盖：{data.route.signal_coverage or '全程基本有信号覆盖'}"
    )
    add_paragraph_styled(doc, route_desc)

    if data.route.gps_track_links:
        add_paragraph_styled(doc, "参考轨迹链接：", bold=True)
        for link in data.route.gps_track_links:
            add_paragraph_styled(doc, f"  - {link}")

    add_paragraph_styled(doc, "（配图位置：卫星路线图 + 高程曲线图）")

    if data.route.segments:
        add_paragraph_styled(doc, "分段详情：", bold=True)
        seg_headers = ["路段", "里程(km)", "爬升(m)", "下降(m)", "路况", "备注"]
        seg_rows = []
        for seg in data.route.segments:
            surface_str = "、".join(seg.surface_types) if seg.surface_types else ""
            hazards_str = "、".join(seg.special_hazards) if seg.special_hazards else ""
            notes = hazards_str + ("；" + seg.description if seg.description else "")
            seg_rows.append([
                seg.name,
                str(seg.distance_km),
                str(seg.elevation_gain_m),
                str(seg.elevation_loss_m),
                surface_str,
                notes,
            ])
        add_table_with_data(doc, seg_headers, seg_rows)

    # 2.2 路线强度
    add_heading_styled(doc, "2. 路线强度", level=2)
    score = data.calc_difficulty_score()
    grade = data.route.difficulty_grade or data.calc_difficulty_grade()
    intensity_text = (
        f"总路线强度 = 路程({data.route.total_distance_km}km) + 爬升({data.route.total_elevation_gain_m}m)/100 = {score:.1f}\n"
        f"路线等级：{grade}"
    )
    add_paragraph_styled(doc, intensity_text)

    add_paragraph_styled(doc, "路线标准强度说明：", bold=True)
    formula_text = (
        "采用 路程(km) + 爬升(m)/100 计算路线强度，\n"
        "休闲 < 12 < 初级 < 20 < 中级 < 35 < 高级 < 50 < 超高级\n"
        "（根据特殊路况，具体分级可作调整）"
    )
    add_paragraph_styled(doc, formula_text)

    # 2.3 路线难度与风险点
    add_heading_styled(doc, "3. 路线难度与风险点", level=2)

    if data.route.surface_summary:
        add_paragraph_styled(doc, f"路面概况：{data.route.surface_summary}")

    if data.route.special_hazards:
        add_paragraph_styled(doc, "特殊路况与风险点：", bold=True)
        for hazard in data.route.special_hazards:
            add_paragraph_styled(doc, f"  - {hazard}")

    if data.route.bailout_routes:
        add_paragraph_styled(doc, "下撤路线：", bold=True)
        for br in data.route.bailout_routes:
            add_paragraph_styled(doc, f"  - {br}")

    add_paragraph_styled(doc, "（配图位置：路线难点照片，帮助队员提前了解）")

    # 2.4 总体评价
    add_heading_styled(doc, "4. 总体评价", level=2)
    if data.route.suitability:
        add_paragraph_styled(doc, data.route.suitability)

    approval_text = "综上所述，路线总风险系数符合日常活动安全管理条例（试行）要求，徒协理事会批准本次活动进行。"
    add_paragraph_styled(doc, approval_text)

    # ============================================================
    # Section 3: 组织事宜
    # ============================================================
    add_heading_styled(doc, "三、组织事宜", level=1)

    # 活动时间
    add_paragraph_styled(doc, f"活动时间：{data.activity.date}（{data.activity.day_of_week}）", bold=True)

    # 领队
    leader_names = " ".join([l.name for l in data.organization.leaders])
    add_paragraph_styled(doc, f"领队：{leader_names}", bold=True)

    # 招募人数
    add_paragraph_styled(doc, f"招募人数：{data.organization.max_participants}人")

    # 预收费用
    cost_lines = [
        f"会员：{data.organization.member_cost}元/人",
        f"非会员：{data.organization.member_cost + data.organization.non_member_surcharge}元/人",
        "（多退少补）",
    ]
    add_paragraph_styled(doc, "预收费用：", bold=True)
    for line in cost_lines:
        add_paragraph_styled(doc, f"  {line}")

    add_paragraph_styled(doc, "费用包含：", bold=True)
    for item in data.organization.cost_includes:
        add_paragraph_styled(doc, f"  - {item}")

    add_paragraph_styled(doc, "费用不包含：", bold=True)
    for item in data.organization.cost_excludes:
        add_paragraph_styled(doc, f"  - {item}")

    # 领队介绍
    add_paragraph_styled(doc, "领队介绍：", bold=True)
    leader_count = len(data.organization.leaders)
    ratio = data.organization.leader_ratio or f"1:{data.organization.max_participants // leader_count}"
    main_leaders = sum(1 for l in data.organization.leaders if l.role == "主领队")
    summary = (
        f"本次活动预计总人数{data.organization.max_participants}人，"
        f"领队{leader_count}人，领队比例{ratio}，"
        f"具有担任主领队资格的领队{main_leaders}人。以下为领队介绍："
    )
    add_paragraph_styled(doc, summary)

    for leader in data.organization.leaders:
        bio_text = f"{leader.name}（{leader.role}）：{leader.bio}"
        add_paragraph_styled(doc, bio_text)

    # 时间安排
    add_paragraph_styled(doc, "时间安排：", bold=True)
    if data.organization.schedule:
        sched_headers = ["时间", "事项"]
        sched_rows = [[s.time, s.activity] for s in data.organization.schedule]
        add_table_with_data(doc, sched_headers, sched_rows, col_widths=[5, 11])

    # 集合地点
    if data.activity.meeting_points:
        add_paragraph_styled(doc, "集合地点：", bold=True)
        for mp in data.activity.meeting_points:
            add_paragraph_styled(doc, f"  {mp.time} —— {mp.location}")

    # 交通方式
    add_paragraph_styled(doc, f"交通方式：{data.activity.transport_mode}前往徒步地点")

    # ============================================================
    # Section 4: 物资准备
    # ============================================================
    add_heading_styled(doc, "四、物资准备", level=1)

    if data.gear:
        category_order = ["必备", "强烈推荐", "可选", "按季节"]
        gear_by_category = {}
        for item in data.gear:
            gear_by_category.setdefault(item.category, []).append(item)

        for cat in category_order:
            items = gear_by_category.pop(cat, [])
            if not items:
                continue
            add_paragraph_styled(doc, f"【{cat}】", bold=True)
            for item in items:
                note_str = f"（{item.notes}）" if item.notes else ""
                add_paragraph_styled(doc, f"  - {item.name}{note_str}")

        for cat, items in gear_by_category.items():
            add_paragraph_styled(doc, f"【{cat}】", bold=True)
            for item in items:
                note_str = f"（{item.notes}）" if item.notes else ""
                add_paragraph_styled(doc, f"  - {item.name}{note_str}")

    # Default gear list if none provided
    if not data.gear:
        add_paragraph_styled(doc, "【必备】", bold=True)
        default_required = [
            "防水防风的外套或雨衣",
            "保暖衣物（抓绒/薄羽绒）",
            "速干长衣长裤（或短袖+袖套）",
            "徒步鞋、越野跑鞋等防滑鞋子",
            "午餐（自备，建议不要自热火锅）",
            "水与功能饮料合计1.5-2L",
        ]
        for item in default_required:
            add_paragraph_styled(doc, f"  - {item}")

        add_paragraph_styled(doc, "【强烈推荐】", bold=True)
        add_paragraph_styled(doc, "  - 登山杖（协会可租借，5元/根）")
        add_paragraph_styled(doc, "  - 护膝")
        add_paragraph_styled(doc, "  - 手台")

        add_paragraph_styled(doc, "【其他】", bold=True)
        add_paragraph_styled(doc, "  - 充电宝、身份证、少量现金、垃圾袋、纸巾/湿巾")

    add_paragraph_styled(doc, "鞋子：推荐穿越野跑鞋、徒步鞋等有一定防滑能力的鞋子，不穿新鞋、板鞋，禁止高跟鞋、拖鞋。鞋底纹路越深越好。")

    # ============================================================
    # Section 5: 报名与注意事项
    # ============================================================
    add_heading_styled(doc, "五、报名与注意事项", level=1)

    add_paragraph_styled(doc, "（报名二维码位置）")

    add_paragraph_styled(doc, "关键时间：", bold=True)
    reg_start = data.activity.registration_start or "【待填写】"
    reg_end = data.activity.registration_end or "【待填写】"
    refund = data.activity.refund_deadline or "【待填写】"
    add_paragraph_styled(doc, f"  报名开始时间：{reg_start}")
    add_paragraph_styled(doc, f"  退款截止时间：{refund}，此后不予退款")
    add_paragraph_styled(doc, f"  报名截止时间：{reg_end}")

    add_paragraph_styled(doc, "注意事项：", bold=True)
    rules = [
        "报名成功后主动扫码进群，修改昵称为【姓名+手机号】，并留意群内通知。",
        "迟到过时不候。",
        "行进时，不超过向导，不落后于押后。",
        "了解户外风险，阅读免责声明。",
        "其他事项可参考常见问答与注意事项，或咨询领队和协会骨干。",
    ]
    for rule in rules:
        add_paragraph_styled(doc, f"  - {rule}")

    if data.registration_notes:
        add_paragraph_styled(doc, data.registration_notes)

    # References
    if data.references_links:
        add_heading_styled(doc, "参考资料", level=2)
        for link in data.references_links:
            add_paragraph_styled(doc, f"  - {link}")

    save_document(doc, output_path)
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_leader_plan.py <input_json> <output_path>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_path = sys.argv[2]

    try:
        data = TrailResearchData.from_json(input_json)
    except Exception as e:
        print(f"Error loading data from {input_json}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = generate_leader_plan(data, output_path)
        print(f"Leader plan saved to: {result}")
    except Exception as e:
        print(f"Error generating leader plan: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
