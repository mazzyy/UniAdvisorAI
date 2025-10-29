from rag_pipeline import DAADCourseRAG

def main():
    """
    Interactive chat interface
    """
    print("="*60)
    print("🎓 DAAD Course Assistant")
    print("="*60)
    print("\nInitializing...")
    
    # Initialize RAG
    rag = DAADCourseRAG()
    rag.load_courses_to_db()
    
    print("\n✅ Ready! Ask me anything about German university courses.")
    print("Type 'quit' to exit\n")
    
    while True:
        # Get user input
        query = input("You: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        # Get answer
        print("\nAssistant: ", end="", flush=True)
        answer = rag.ask(query)
        print(answer)
        print()


if __name__ == "__main__":
    main()