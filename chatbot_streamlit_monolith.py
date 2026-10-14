import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()


@st.cache_resource
def get_model():
    return ChatGroq(model="openai/gpt-oss-120b")


# Streamlit har interaction pe poori file dobara chalata hai.
# @st.cache_resource model ko sirf EK baar banata hai aur baad ke reruns mein
# wahi purana object wapas deta hai (naya ChatGroq nahi banta).

# model = get_model() function call karta hai, jo ChatGroq object return karta hai.
# @st.cache_resource is function ko pehli baar hi chalne deta hai aur uska result
# apne cache mein save kar leta hai. Agli har call pe (har rerun pe) wahi saved
# object wapas mil jaata hai, function dobara nahi chalta — naya object nahi banta.


model = get_model()

st.header("CHAT-BHAI", text_alignment="center")

# History sirf pehli baar banegi, uske baad reruns mein bachi rahegi
if "chat_history" not in st.session_state:  # st.session_state = return type dict
    st.session_state.chat_history = [
        SystemMessage(
            "You are an AI assistant named 'Chat-Bhai'. Do not use LaTeX, reply in plain text."
        )
    ]
# session_state ek dictionary jaisa hai jo Streamlit ke reruns ke beech bachi rehti hai
# (normal variables har rerun pe reset ho jaate hain, session_state nahi).
# Check karo: "chat_history" key pehle se maujood hai kya?
# - Pehli baar (app khulte hi): nahi hai, to list banti hai, sirf SystemMessage ke saath.
# - Baad ke har rerun: key already hai, is if ke andar ka code skip ho jaata hai,
#   purani history jaisi thi waisi hi rehti hai.


# runs only jab chathistory hogi
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# chat_history list mein 3 tarah ke objects hote hain:
# SystemMessage, HumanMessage, AIMessage (LangChain ki classes)
# isinstance() check karta hai ki 'msg' kis class ka object hai,
# taaki uske hisaab se sahi chat bubble (user/assistant) banaya ja sake.
# SystemMessage kisi if/elif mein match nahi hota, isliye screen pe nahi dikhta.
#
# st.chat_message("user") ek bubble/container banata hai (user ka avatar/logo ke saath).
# 'with' ye batata hai ki andar ka indented code isi bubble ke ANDAR render hoga.
# with block khatam hote hi bubble bhi "band" ho jaata hai (jaise file open-close hota hai).
# st.write(msg.content) us bubble ke andar msg ka asli text likh deta hai.


# st.chat_input() user ka text return karta hai (terminal ke input() jaisa).
# Sirf us ek rerun mein text milta hai jab user Enter dabaye, baaki reruns mein None
# aata hai, isliye if lagaya: naya message aaye tabhi andar ka code chale.
if user_input := st.chat_input("Ask bro..."):
    # Naya HumanMessage history list mein jodo, taaki agle rerun pe for loop
    # use "purani chat" ki tarah dikha sake, aur model.invoke ko bhi context mile.
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.write(user_input)

    # Poori history model ko bhejo (yahin asli API call hoti hai).
    # Isi se model ko purani baatein yaad rehti hain.
    result = model.invoke(st.session_state.chat_history)

    # Model ka jawab AIMessage banake history mein jodo (agle rerun ke liye).
    st.session_state.chat_history.append(AIMessage(content=result.content))
    with st.chat_message("assistant"):
        st.write(result.content)

    # Ye line invoke ke BAAD chalti hai, isliye is jawab ka context isi call ke liye
    # LLM ko nahi jaata (aur chahiye bhi nahi, jawab LLM ne abhi khud diya hai).
    # Iska kaam AGLE message ke liye hai: agli baar invoke ko poori list jayegi,
    # jisme LLM ka pichla jawab bhi hoga, isi se usko conversation yaad rehti hai.
    # Ye append na ho to LLM apne purane jawab bhool jayega.
