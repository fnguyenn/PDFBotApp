# langchain_pipeline.py
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Takes raw text and returns a LangChain pipeline that can answer questions based on it
def build_qa_chain(text):
    try:
        # creates a text splitter that breaks long text into chunks of 500 characters, with 50 characters of overlap to preserve context
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.create_documents([text])        # splits the input text into a list of LangChain document objects


        embeddings = OpenAIEmbeddings()    # OpenAI’s embedding model to convert text into high-dimensional vectors
        vectorstore = FAISS.from_documents(docs, embedding=embeddings) # converts the split docs into vector embeddings and stores them in a FAISS index for fast similarity search
        retriever = vectorstore.as_retriever()      # will be used to look up relevant text chunks in response to a question


        # defines a reusable prompt that the language model will see
        prompt = PromptTemplate.from_template("""
        You are a helpful assistant. Use the following context to answer the question.
        
        Context:
        {context}

        Question:
        {question}

        Answer:
        """)


        llm = ChatOpenAI(model="gpt-4") # initializes the GPT-4 model from OpenAI using LangChain’s wrapper


        # builds a LangChain Expression Language chain
        # 1.takes user input, passes it to the retriever to fetch context, and passes the question directly
        # 2.fills the prompt template with {context} and {question}
        # 3.sends the filled prompt to GPT-4 for an answer
        # 4.extracts the model’s answer as a plain string
        chain = (
            {"context": retriever | RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        return chain
    except Exception as e:
        raise RuntimeError(f"Failed to build QA chain: {e}")