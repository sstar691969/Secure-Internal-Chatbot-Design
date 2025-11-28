# Secure-Internal-Chatbot Design:Weekly injury update

William Anderson
Kyle Kitching
Michael Tamirat
Victoria salomon


# Secure-Internal-Chatbot-Design
chatbot-Weekly injury update

All Functional prototype source code demonstrating at least one core interaction (e.g., secure login, internal Q&A).
A README.md file with:


Description:

The Sentinel Internal Chatbot is a demo application designed to simulate a secure, role-based chat platform for a fictional sports team. It demonstrates how internal staff — like team physicians, coaches, and trainers — can interact with a chatbot to access and update player injury reports in real time.

Key features demonstrated:

Role-based access control: Depending on your role (Team Physician, Coach, etc.), the chatbot tailors responses and permissions. For example, only Team Physicians can update injury details, while other roles can view but not modify sensitive information.

Session management: The app maintains session state for each user, including login, multi-factor authentication simulation, and chat history.

Live injury updates: Team Physicians can modify player injury data directly from the interface, and the chatbot reflects these updates immediately.

Query logging: Every question or update is logged into a demo “query database” for analysis, showing how internal queries could be tracked without exposing sensitive patient data.

Security demonstration: Although this is a prototype with fictional data, it highlights sensitive data segregation and role-aware access, mimicking how protected health information (PHI) could be safely handled in a real system.
Technologies used (Python-3.10/Streamlit, GPT-2.
