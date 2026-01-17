import streamlit as st
import json
import random
import time
import sys
sys.path.append('.') 
from typing import List, Dict
try:
    from utils.validator import validate_poem_data, get_poem_stats
except ImportError:
    # 如果utils模块不存在，使用空函数
    def validate_poem_data(poem):
        return True, "验证跳过"
    def get_poem_stats(poems):
        return {'total': len(poems)}

# 页面配置
st.set_page_config(
    page_title="AI唐诗工坊",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 自定义CSS
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        text-align: center;
        color: #1E3A8A;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    /* 卡片样式 */
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #4F46E5;
    }
    
    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# 加载诗歌数据
@st.cache_data
def load_poems():
    """加载唐诗数据"""
    try:
        with open('data/poems.json', 'r', encoding='utf-8') as f:
            poems = json.load(f)
        if not poems:
            st.warning("数据文件为空，请检查data/poems.json")
            return []
        return poems
    except FileNotFoundError:
        st.error("❌ 未找到数据文件！请确保 data/poems.json 存在")
        return []
    except json.JSONDecodeError:
        st.error("❌ 数据文件格式错误！请检查JSON格式")
        return []
    except Exception as e:
        st.error(f"❌ 加载数据时发生未知错误: {e}")
        return []

# 初始化session state
if 'challenge_poem' not in st.session_state:
    st.session_state.challenge_poem = None
    st.session_state.show_answer = False
    st.session_state.score = 0
    st.session_state.total_attempts = 0
    st.session_state.user_answers = []

# 侧边栏导航
st.sidebar.title("🎭 AI唐诗工坊")
st.sidebar.image("https://img.icons8.com/color/96/000000/china.png", width=80)
app_mode = st.sidebar.selectbox(
    "选择功能",
    ["🏠 首页", "📖 智能赏析", "🏆 对诗挑战", "✍️ AI创作", "📊 学习报告"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
### 项目特点
- 🤖 AI智能赏析
- 🎯 互动对诗挑战
- ✨ AI诗歌创作
- 📈 学习进度追踪
""")

# 加载数据
poems = load_poems()

# 首页
if app_mode == "🏠 首页":
    st.title("🎭 AI唐诗工坊")
    st.markdown("### 融合AI技术的唐诗学习与创作平台")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📖 智能赏析")
        st.markdown("""
        - 深度解析唐诗内涵
        - AI生成扩展解读
        - 多维度诗歌分析
        """)
        if st.button("开始赏析", key="home_appreciation"):
            st.session_state.app_mode = "📖 智能赏析"
            st.rerun()
    
    with col2:
        st.markdown("### 🏆 对诗挑战")
        st.markdown("""
        - 诗句填空挑战
        - 实时评分系统
        - 错题回顾功能
        """)
        if st.button("开始挑战", key="home_challenge"):
            st.session_state.app_mode = "🏆 对诗挑战"
            st.rerun()
    
    with col3:
        st.markdown("### ✍️ AI创作")
        st.markdown("""
        - AI辅助诗歌创作
        - 自定义创作主题
        - 多风格选择
        """)
        if st.button("开始创作", key="home_creation"):
            st.session_state.app_mode = "✍️ AI创作"
            st.rerun()
    
    st.markdown("---")
    
    # 展示部分唐诗
    st.subheader("📚 唐诗精选")
    if poems:
        cols = st.columns(3)
        for idx, poem in enumerate(poems[:3]):
            with cols[idx]:
                with st.container():
                    st.markdown(f"**{poem['title']}**")
                    st.markdown(f"*{poem['author']}（{poem['dynasty']}）*")
                    st.markdown(f"> {poem['content'][:15]}...")
                    if st.button(f"赏析此诗", key=f"quick_{idx}"):
                        st.session_state.app_mode = "📖 智能赏析"
                        st.session_state.selected_poem_idx = idx
                        st.rerun()

# 智能赏析功能
elif app_mode == "📖 智能赏析":
    st.header("📖 智能赏析")
    st.markdown("选择一首唐诗，获取AI的深度解析与赏析。")
    
    if not poems:
        st.warning("暂无诗歌数据，请检查数据文件")
        st.stop()
    
    # 诗歌选择
    poem_options = [f"{poem['title']} - {poem['author']}" for poem in poems]
    selected_title = st.selectbox("选择一首唐诗", poem_options)
    
    if selected_title:
        # 获取选中的诗歌
        selected_idx = next(i for i, poem in enumerate(poems) 
                           if f"{poem['title']} - {poem['author']}" == selected_title)
        poem = poems[selected_idx]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(poem['title'])
            st.markdown(f"**作者**：{poem['author']}")
            st.markdown(f"**朝代**：{poem['dynasty']}")
            
            st.markdown("### 原文")
            # 处理诗句显示，每句一行
            lines = poem['content'].replace('。', '。\n').replace('，', '，\n').split('\n')
            for line in lines:
                if line.strip():
                    st.markdown(f"**{line.strip()}**")
            
            st.markdown("---")
            st.markdown("### 基本信息")
            st.info(f"**诗歌类型**：五言绝句")
            st.info(f"**创作背景**：{random.choice(['山水田园', '思乡怀人', '边塞征战', '咏物言志'])}诗")
        
        with col2:
            st.subheader("AI深度解析")
            
            with st.expander("📝 白话译文", expanded=True):
                st.success(poem['translation'])
            
            with st.expander("🎨 诗歌赏析", expanded=True):
                st.info(poem['explanation'])
            
            with st.expander("💡 AI扩展解读"):
                # 模拟AI生成的扩展内容
                themes = {
                    "静夜思": ["思乡之情", "月光意象", "游子情怀"],
                    "春晓": ["惜春之感", "自然之美", "时光流逝"],
                    "登鹳雀楼": ["登高望远", "人生哲理", "进取精神"],
                    "悯农": ["民生关怀", "劳动价值", "节约意识"],
                    "江雪": ["孤寂之境", "坚韧品格", "冬日景象"]
                }
                
                poem_themes = themes.get(poem['title'], ["古典之美", "诗意情怀"])
                
                st.markdown("#### 核心主题")
                for theme in poem_themes:
                    st.markdown(f"- **{theme}**：{random.choice(['贯穿全诗', '点睛之笔', '情感核心'])}")
                
                st.markdown("#### 艺术特色")
                art_features = [
                    f"**语言风格**：{random.choice(['清新自然', '雄浑豪放', '婉约含蓄'])}",
                    f"**修辞手法**：{random.choice(['比喻', '拟人', '对偶'])}的巧妙运用",
                    f"**意象选择**：{random.choice(['自然意象', '人文意象', '情感意象'])}的精准把握"
                ]
                for feature in art_features:
                    st.markdown(f"- {feature}")
            
            with st.expander("📚 关联学习"):
                # 推荐相关诗歌
                related_poems = [p for p in poems if p['author'] == poem['author'] and p['title'] != poem['title']]
                if related_poems:
                    st.markdown("#### 同作者作品")
                    for rp in related_poems[:2]:
                        st.markdown(f"- **{rp['title']}**：{rp['content'][:10]}...")
                
                st.markdown("#### 学习建议")
                st.markdown("""
                1. 尝试背诵全诗
                2. 理解诗歌创作背景
                3. 体会诗人情感表达
                4. 学习诗歌的格律特点
                """)

# 对诗挑战功能
elif app_mode == "🏆 对诗挑战":
    st.header("🏆 对诗挑战")
    st.markdown("测试你对唐诗的掌握程度，看看你能答对多少！")
    
    if not poems:
        st.warning("暂无诗歌数据，请检查数据文件")
        st.stop()
    
    # 挑战控制面板
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 开始新挑战", use_container_width=True):
            st.session_state.challenge_poem = random.choice(poems)
            st.session_state.show_answer = False
            st.session_state.current_answer = ""
            st.rerun()
    
    with col2:
        if st.button("🔄 换一首诗", use_container_width=True) and st.session_state.challenge_poem:
            st.session_state.challenge_poem = random.choice(poems)
            st.session_state.show_answer = False
            st.session_state.current_answer = ""
            st.rerun()
    
    with col3:
        if st.button("📊 查看成绩", use_container_width=True):
            st.session_state.show_score = True
            st.rerun()
    
    # 显示当前挑战
    if st.session_state.challenge_poem:
        poem = st.session_state.challenge_poem
        
        st.divider()
        st.subheader("挑战题目")
        
        col_info, col_poem = st.columns([1, 2])
        
        with col_info:
            st.markdown(f"**诗歌**：{poem['title']}")
            st.markdown(f"**作者**：{poem['author']}")
            st.markdown(f"**难度**：⭐{'⭐' * random.randint(1, 3)}")
        
        with col_poem:
            # 创建填空
            content = poem['content']
            # 随机选择一句进行填空
            sentences = [s for s in content.split('。') if s]
            if sentences:
                target_sentence = random.choice(sentences)
                # 随机隐藏一部分
                words = list(target_sentence.replace('，', ''))
                hidden_indices = random.sample(range(len(words)), min(3, len(words)))
                
                display_sentence = ""
                for i, char in enumerate(words):
                    if i in hidden_indices:
                        display_sentence += "___"
                    else:
                        display_sentence += char
                
                st.markdown(f"**诗句填空**：")
                st.markdown(f"> {display_sentence}")
        
        # 用户输入
        user_answer = st.text_input("请输入完整的隐藏诗句：", 
                                   key="current_answer",
                                   placeholder="请输入完整的诗句...")
        
        # 提交答案
        col_submit, col_show = st.columns(2)
        
        with col_submit:
            if st.button("📤 提交答案", use_container_width=True):
                if user_answer.strip():
                    st.session_state.total_attempts += 1
                    
                    # 简单判断答案
                    if user_answer.strip() == target_sentence:
                        st.session_state.score += 1
                        st.session_state.user_answers.append({
                            "poem": poem['title'],
                            "user_answer": user_answer,
                            "correct": True,
                            "correct_answer": target_sentence
                        })
                        st.success("✅ 回答正确！")
                    else:
                        st.session_state.user_answers.append({
                            "poem": poem['title'],
                            "user_answer": user_answer,
                            "correct": False,
                            "correct_answer": target_sentence
                        })
                        st.error("❌ 回答错误")
                    
                    st.session_state.show_answer = True
                    st.rerun()
                else:
                    st.warning("请先输入答案")
        
        with col_show:
            if st.button("👁️ 显示答案", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        
        # 显示答案
        if st.session_state.show_answer:
            st.divider()
            col_answer, col_explanation = st.columns(2)
            
            with col_answer:
                st.markdown("### 正确答案")
                st.success(f"**{target_sentence}**")
                
                st.markdown("### 完整诗歌")
                st.info(poem['content'])
            
            with col_explanation:
                st.markdown("### 诗歌赏析")
                st.markdown(poem['explanation'][:100] + "...")
                
                if st.button("📖 查看完整赏析"):
                    st.session_state.app_mode = "📖 智能赏析"
                    selected_idx = next(i for i, p in enumerate(poems) if p['title'] == poem['title'])
                    st.session_state.selected_poem_idx = selected_idx
                    st.rerun()
    
    # 成绩显示
    st.divider()
    col_score, col_progress = st.columns(2)
    
    with col_score:
        st.metric("当前得分", f"{st.session_state.score}分")
        st.metric("挑战次数", st.session_state.total_attempts)
    
    with col_progress:
        if st.session_state.total_attempts > 0:
            accuracy = (st.session_state.score / st.session_state.total_attempts) * 100
            st.metric("正确率", f"{accuracy:.1f}%")
            st.progress(accuracy / 100)
    
    # 答题记录
    if st.session_state.user_answers:
        with st.expander("📝 查看答题记录"):
            for i, record in enumerate(st.session_state.user_answers[-5:]):  # 显示最近5条
                status = "✅" if record['correct'] else "❌"
                st.markdown(f"{status} **{record['poem']}**")
                st.markdown(f"你的答案：{record['user_answer']}")
                if not record['correct']:
                    st.markdown(f"正确答案：{record['correct_answer']}")
                st.markdown("---")

# AI创作功能
elif app_mode == "✍️ AI创作":
    st.header("✍️ AI诗歌创作")
    st.markdown("输入主题，让AI为你创作一首唐诗！")
    
    # 创作设置
    col_settings, col_preview = st.columns([1, 1])
    
    with col_settings:
        # 主题选择
        themes = ["山水田园", "思乡怀人", "边塞征战", "咏物言志", "送别友情", "爱情闺怨", "咏史怀古", "节日时令"]
        selected_themes = st.multiselect("选择创作主题（可多选）", themes, default=["山水田园"])
        
        # 风格选择
        style = st.selectbox("选择诗歌风格", 
                           ["豪放飘逸", "沉郁顿挫", "清新自然", "婉约细腻", "雄浑壮阔"])
        
        # 关键词输入
        keywords = st.text_input("输入关键词（用逗号分隔）", 
                                "明月,青山,流水,秋风")
        
        # 创作按钮
        if st.button("✨ 开始创作", use_container_width=True):
            if not selected_themes:
                st.warning("请至少选择一个主题！")
            else:
                st.session_state.creating = True
                st.rerun()
    
    # 创作过程
    if st.session_state.get('creating', False):
        st.divider()
        
        # 模拟AI创作过程
        with st.spinner("AI诗人正在创作中..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(1, 101):
                time.sleep(0.03)
                progress_bar.progress(i)
                
                if i < 30:
                    status_text.text("正在构思主题...")
                elif i < 60:
                    status_text.text("正在推敲词句...")
                elif i < 90:
                    status_text.text("正在调整韵律...")
                else:
                    status_text.text("创作完成！")
            
            time.sleep(0.5)
        
        # 显示创作结果
        st.success("🎉 创作完成！")
        
        # 生成AI诗歌
        poem_templates = [
            {
                "title": "秋夜思",
                "content": "明月照高楼，清辉洒九州。\n思君如满月，夜夜减清辉。\n秋风起天末，游子意如何？\n鸿雁几时到，江湖秋水多。",
                "explanation": "此诗以秋夜为背景，通过明月、秋风、鸿雁等意象，表达了深切的思乡之情和游子情怀。"
            },
            {
                "title": "山居春晓",
                "content": "春山多胜事，赏玩夜忘归。\n掬水月在手，弄花香满衣。\n兴来无远近，欲去惜芳菲。\n南望鸣钟处，楼台深翠微。",
                "explanation": "描绘春日山居的乐趣，展现人与自然和谐相处的意境。"
            },
            {
                "title": "江畔送别",
                "content": "杨柳渡头行客稀，罟师荡桨向临圻。\n唯有相思似春色，江南江北送君归。",
                "explanation": "以春色喻相思，表达送别友人时的不舍之情。"
            }
        ]
        
        ai_poem = random.choice(poem_templates)
        
        # 根据主题调整标题
        if "山水" in "".join(selected_themes):
            ai_poem["title"] = random.choice(["山水吟", "登高望远", "江山如画"])
        elif "思乡" in "".join(selected_themes):
            ai_poem["title"] = random.choice(["秋夜思", "乡愁", "月夜忆舍弟"])
        
        col_result, col_analysis = st.columns([1, 1])
        
        with col_result:
            st.subheader("AI原创诗歌")
            st.markdown(f"### {ai_poem['title']}")
            st.markdown(f"*作者：AI诗人*")
            
            st.markdown("```")
            for line in ai_poem['content'].split('\n'):
                st.markdown(line)
            st.markdown("```")
            
            # 下载功能
            poem_text = f"{ai_poem['title']}\n\n{ai_poem['content']}\n\n——AI诗人创作"
            st.download_button(
                label="📥 下载诗歌",
                data=poem_text,
                file_name=f"{ai_poem['title']}.txt",
                mime="text/plain"
            )
        
        with col_analysis:
            st.subheader("创作分析")
            
            st.markdown("### 创作参数")
            st.info(f"**主题**：{', '.join(selected_themes)}")
            st.info(f"**风格**：{style}")
            if keywords:
                st.info(f"**关键词**：{keywords}")
            
            st.markdown("### AI创作说明")
            st.success(ai_poem['explanation'])
            
            st.markdown("### 创作亮点")
            highlights = [
                f"运用了{random.choice(['对仗', '比喻', '拟人'])}修辞手法",
                f"体现了{style}的诗歌风格",
                f"融入了{random.choice(selected_themes)}的典型意象",
                "符合唐代诗歌的韵律要求"
            ]
            for highlight in highlights:
                st.markdown(f"✅ {highlight}")
        
        # 评价功能
        st.divider()
        st.subheader("评价AI创作")
        
        col_rating, col_feedback = st.columns([1, 2])
        
        with col_rating:
            rating = st.slider("请为这首诗打分", 1, 5, 4)
            if st.button("提交评分"):
                st.balloons()
                st.success(f"感谢评价！你给出了{rating}星评价。")
        
        with col_feedback:
            feedback = st.text_area("你的建议（可选）", 
                                   placeholder="这首诗有什么可以改进的地方？")
            if st.button("提交建议"):
                if feedback:
                    st.success("感谢你的宝贵建议！")

# 学习报告功能
elif app_mode == "📊 学习报告":
    st.header("📊 学习报告")
    st.markdown("查看你的学习进度和成就")
    
    if not poems:
        st.warning("暂无学习数据")
        st.stop()
    
    # 学习统计
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("已学习诗歌", f"{len(poems)}首")
    
    with col_stats2:
        if st.session_state.total_attempts > 0:
            accuracy = (st.session_state.score / st.session_state.total_attempts) * 100
            st.metric("挑战正确率", f"{accuracy:.1f}%")
        else:
            st.metric("挑战正确率", "0%")
    
    with col_stats3:
        st.metric("创作次数", st.session_state.get('creation_count', 0))
    
    # 学习进度
    st.divider()
    st.subheader("学习进度")
    
    # 诗歌掌握情况
    st.markdown("### 诗歌掌握情况")
    for i, poem in enumerate(poems):
        col_poem, col_progress = st.columns([2, 3])
        
        with col_poem:
            st.markdown(f"**{poem['title']}** - {poem['author']}")
        
        with col_progress:
            # 随机生成掌握程度（模拟数据）
            mastery = random.randint(30, 100)
            st.progress(mastery / 100)
            st.caption(f"{mastery}%")
    
    # 答题历史
    st.divider()
    if st.session_state.user_answers:
        st.subheader("最近答题记录")
        
        for record in st.session_state.user_answers[-3:]:
            col_icon, col_content = st.columns([1, 10])
            
            with col_icon:
                if record['correct']:
                    st.success("✅")
                else:
                    st.error("❌")
            
            with col_content:
                st.markdown(f"**{record['poem']}**")
                st.markdown(f"你的答案：{record['user_answer']}")
                if not record['correct']:
                    st.markdown(f"正确答案：{record['correct_answer']}")
                st.markdown("---")
    
    # 导出报告
    st.divider()
    if st.button("📄 生成学习报告", use_container_width=True):
        report_content = f"""
        AI唐诗工坊学习报告
        ===================
        
        学习概况：
        - 学习诗歌：{len(poems)}首
        - 挑战次数：{st.session_state.total_attempts}次
        - 得分：{st.session_state.score}分
        - 正确率：{(st.session_state.score/st.session_state.total_attempts*100 if st.session_state.total_attempts > 0 else 0):.1f}%
        
        已学习诗歌：
        {chr(10).join([f"- {poem['title']} ({poem['author']})" for poem in poems])}
        
        学习建议：
        1. 坚持每日学习一首新诗
        2. 定期复习已学诗歌
        3. 多参与对诗挑战
        4. 尝试创作自己的诗歌
        
        生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        st.download_button(
            label="📥 下载学习报告",
            data=report_content,
            file_name="唐诗学习报告.txt",
            mime="text/plain"
        )

# 页脚
st.divider()
st.caption("🎭 AI唐诗工坊 | 基于Streamlit开发 | © 2023 唐诗学习助手")

# 初始化session state
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "🏠 首页"
if 'selected_poem_idx' not in st.session_state:
    st.session_state.selected_poem_idx = 0
if 'creation_count' not in st.session_state:
    st.session_state.creation_count = 0