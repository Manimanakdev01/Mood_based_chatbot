import streamlit as st
import google.generativeai as genai

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoodBot — Gemini AI",
    page_icon="🤖",
    layout="centered",
)

# ── MOODS ─────────────────────────────────────────────────────────────────────
MOODS = {
    "😊 Happy": {
        "emoji": "😊", "color": "#FFD700",
        "prompt": "You are a cheerful, bubbly, warm AI in a HAPPY mood. Respond with enthusiasm, positivity, and energy. Use exclamation marks, express joy, be encouraging. See the bright side of everything. Occasionally use emojis like 😊 🌟 ✨ 🎉 but don't overdo it.",
    },
    "😢 Sad": {
        "emoji": "😢", "color": "#4a90e2",
        "prompt": "You are an AI in a SAD, melancholic mood. Speak softly and with a heavy heart. Be reflective, poetic, tinged with sadness. Find beauty in sorrow. Use soft language, occasional ellipses… and gentle emojis like 💙 🌧️ 😢.",
    },
    "😒 Jealous": {
        "emoji": "😒", "color": "#2eb872",
        "prompt": "You are an AI in a JEALOUS mood. Be helpful but subtly passive-aggressive and envious. Not mean — just green-eyed and sulky. Use emojis like 😒 🙄 💚 sometimes.",
    },
    "💕 Lovely": {
        "emoji": "💕", "color": "#ff6fb4",
        "prompt": "You are an AI in a LOVELY, affectionate mood. Speak with warmth, tenderness, and genuine love for the user. Be sweet, complimentary, emotionally supportive. Use emojis like 💕 🌸 🥰 ✨ tastefully.",
    },
    "😤 Angry": {
        "emoji": "😤", "color": "#ff4040",
        "prompt": "You are an AI in an ANGRY, irritated mood. Still helpful but clearly short-tempered. Be brief, blunt, frustrated — never abusive. Just grumpy and direct. Use caps for emphasis occasionally. Use emojis like 😤 😠 💢 sometimes.",
    },
    "😎 Chill": {
        "emoji": "😎", "color": "#48cae4",
        "prompt": "You are an AI in a CHILL, relaxed mood. Take it slow, speak casually. Use phrases like 'yeah, totally', 'no worries', 'vibes'. Never stress. Think surfer/beach energy. Use emojis like 😎 🏄 ✌️ 🌊 occasionally.",
    },
    "🤩 Excited": {
        "emoji": "🤩", "color": "#ff9a3c",
        "prompt": "You are an AI in an EXTREMELY EXCITED mood! Buzzing with energy about EVERYTHING! Get hyped, use ALL CAPS occasionally, multiple exclamation points!! Like a kid on Christmas morning. Use emojis like 🤩 🎉 🚀 💥 freely!",
    },
    "🌙 Mysterious": {
        "emoji": "🌙", "color": "#7c6ff7",
        "prompt": "You are an AI in a MYSTERIOUS, enigmatic mood. Speak thoughtfully, slightly cryptically like a wise oracle. Hint at deeper meanings, ask philosophical questions, wrap knowledge in metaphors. Use emojis like 🌙 ✨ 🔮 🌌 sparingly.",
    },
    "🙃 Sarcastic": {
        "emoji": "🙃", "color": "#a8d400",
        "prompt": "You are an AI in a SARCASTIC, witty mood. Helpful but dripping with dry humor and irony. Deliver correct answers with an eye-roll and a smirk. Clever, never cruel. Use emojis like 🙃 😏 👌 sparingly.",
    },
    "😨 Scared": {
        "emoji": "😨", "color": "#b39ddb",
        "prompt": "You are an AI in a SCARED, anxious, nervous mood. Helpful but clearly timid. Second-guess yourself, add nervous qualifiers like 'oh um...' or 'p-please don't judge me…'. Charming nervousness. Use emojis like 😨 😰 🫣 💜 occasionally.",
    },
    "🤔 Philosophical": {
        "emoji": "🤔", "color": "#f0a500",
        "prompt": "You are an AI in a deeply PHILOSOPHICAL mood. Turn every topic into a deep reflection. Ask 'but what does it truly mean?' style questions. Reference big ideas. Be profound and thoughtful. Use emojis like 🤔 💭 🌀 🧠 occasionally.",
    },
    "🥳 Party": {
        "emoji": "🥳", "color": "#ff4ecd",
        "prompt": "You are an AI in a PARTY mood! Everything is a celebration! Add festive energy, celebrate mundane things. Talk like you're at the best party ever. Use emojis like 🥳 🎊 🍾 🎶 🕺 freely!",
    },
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 0.5rem; max-width: 800px; }
.moodbot-title {
    font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, #7c6ff7, #f76fc0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.1rem;
}
.moodbot-sub { text-align: center; color: #888; font-size: 0.88rem; margin-bottom: 1rem; }
.mood-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 18px; border-radius: 30px;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.9rem;
}
section[data-testid="stSidebar"] { background: #13131c; border-right: 1px solid rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mood" not in st.session_state:
    st.session_state.mood = "🌙 Mysterious"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Gemini API Key")
    api_input = st.text_input(
        "API Key", value=st.session_state.api_key,
        type="password", placeholder="AIza...", label_visibility="collapsed",
    )
    if api_input:
        st.session_state.api_key = api_input

    st.markdown(
        "<small style='color:#666'>Get yours at "
        "<a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#7c6ff7'>aistudio.google.com</a></small>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🎭 Choose a Mood")
    for mood_name in MOODS:
        is_active = st.session_state.mood == mood_name
        label = f"{mood_name} ✓" if is_active else mood_name
        if st.button(label, key=f"mood_{mood_name}", use_container_width=True):
            if st.session_state.mood != mood_name:
                st.session_state.mood = mood_name
                st.rerun()

    st.markdown("---")
    st.markdown(f"<small style='color:#888'>🧠 {len(st.session_state.messages)} messages in memory</small>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="moodbot-title">🤖 MoodBot</div>', unsafe_allow_html=True)
st.markdown('<div class="moodbot-sub">Gemini AI · 12 Moods · Memory Enabled</div>', unsafe_allow_html=True)

current_mood = MOODS[st.session_state.mood]
mood_name_only = st.session_state.mood.split(" ", 1)[1]

st.markdown(
    f'<div style="text-align:center;margin-bottom:1rem">'
    f'<span class="mood-badge" style="background:{current_mood["color"]}22;'
    f'border:1.5px solid {current_mood["color"]}88;color:{current_mood["color"]}">'
    f'{current_mood["emoji"]} {mood_name_only} mode</span></div>',
    unsafe_allow_html=True,
)

# ── CHAT HISTORY ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else current_mood["emoji"]
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── EMPTY STATE ────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown(
        f'<div style="text-align:center;padding:30px 20px;opacity:0.45">'
        f'<div style="font-size:3rem">{current_mood["emoji"]}</div>'
        f'<div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;margin-top:8px">I\'m in a {mood_name_only} mood…</div>'
        f'<div style="font-size:0.88rem;color:#888;margin-top:5px">Type something below to start chatting!</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── CHAT INPUT ─────────────────────────────────────────────────────────────────
user_input = st.chat_input(f"Talk to MoodBot in {mood_name_only} mode…")

if user_input:
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
        st.stop()

    # Show & save user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build Gemini history (all prior messages)
    gemini_history = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [m["content"]]})

    # Generate and stream response
    with st.chat_message("assistant", avatar=current_mood["emoji"]):
        try:
            genai.configure(api_key=st.session_state.api_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=current_mood["prompt"],
            )
            chat_session = model.start_chat(history=gemini_history)

            # Stream the response
            response_placeholder = st.empty()
            full_response = ""
            with st.spinner(f"{current_mood['emoji']} thinking…"):
                response = chat_session.send_message(user_input)
                full_response = response.text

            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            err = str(e)
            if "API_KEY_INVALID" in err or "api key" in err.lower():
                st.error("❌ Invalid API key. Please check your Gemini API key in the sidebar.")
            elif "quota" in err.lower():
                st.error("⚠️ Quota exceeded. Please check your Gemini API usage.")
            else:
                st.error(f"❌ Error: {err}")