This is an interactable Bookstore database manager based on tkinter. This code was based on a project for the Department of Anthropology, Digital Archaeology Lab at Northern Arizona University in Flagstaff. My former supervisor has permitted me to use this code on my work portfolio as long as changes and addditions made to it, which both have been made.


This application implements the standard CRUD interface (Create, Read, Update, Delete). It can handle insertion, editing, and deleting of rows. It is not perfect because if you select a row to edit but have a different table selected from the drop down menu, it will bring up parameters for entries for that table instead of the one currently shown. I will fix this when I have more time.

The UI for this project was developed using a research-driven approach, combining official Tkinter documentation with AI-augmented refactoring (ChatGPT). I utilized LLMs to audit early prototypes, transitioning the codebase from basic data insertion to a complete CRUD interface. To ensure code quality and system reliability, I performed a detailed analysis of all suggested logic, ensuring I could verify and explain the architectural choices. This allowed me to treat the AI as a technical peer—leveraging it for rapid prototyping while maintaining absolute ownership of the final implementation.

To use the code, you just need the ui.py file and the .db file next to it, and run "python3 ui.py". I have only tested this app with the lastest version of python3, so I will say that it only works with that, to be safe.
