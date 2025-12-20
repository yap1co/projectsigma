Year 11 and Year 12 students in the UK frequently struggle to identify suitable university courses due to the overwhelming number of options. Factors such as course content, predicted/ucas application grades, A-level subjects, geographical preferences, tuition fees, entrance exams, university prestige, and employability make the choice extremely complex and stressful. 
While existing tools like Discover Uni provide trusted course information, they do not match courses to a student’s unique combination of A-level subjects, predicted grades, and personal priorities. As a result, students must manually filter and compare options, risking overlooked details or leading to unsuitable choices. My proposed system plans to bridge this gap by providing an personalised recommendation engine that automatically ranks courses based on each student’s academic profile and preferences, helping them fill the slots of the 5 universities to which they will apply.
1.4	Intended Users
The primary intended users are Year 11-13 students across UK secondary schools but focusing on my own school for accessibility. I have chosen two students from my school to have an in-depth interview with, namely: Sofia Ansell and Chloé Masson. Both are prefects and early applicants meaning they will be close to finishing their application by the time I interview them, giving a special overview on their struggles and resources they found most helpful.

I propose developing a browser-based full-stack application.
After evaluating the options, the Full-Stack Web Application (Option 3) has been chosen. This approach provides the most professional, user accessible and feature-rich solution that directly meets the needs of the intended users such as students, teachers, and parents who expect modern, browser-based tools.  The key reasons for this choice are:
Python Backend: My existing knowledge of Python makes it the ideal choice for the backend. Using a lightweight framework like Flask will allow me to build a powerful API to handle the recommendation logic and database queries efficiently. This will allow me to demonstrate advanced Object-Oriented Programming skills.
React Frontend: A JavaScript framework like React enables the creation of a dynamic and interactive user interface. This will help deliver features like real-time filtering and sorting of results, providing a better user experience than a server-rendered site. This demonstrates a separation of concerns between the client-side and server-side.
MongoDB Database: A NoSQL database like MongoDB is perfectly suited for this project. University course data is often complex, semi-structured and have campus image. MongoDB's flexible document model allows for storing all information about a university as well as course—including nested data like entry requirements for different qualifications—in a single record, which is more efficient than a SQL tabular schema for this use case.
While this approach is ambitious, it provides the best opportunity to develop a high-quality solution and demonstrate a comprehensive range of advanced technical skills relevant to the AQA A-level Computer Science specification.
Overall layout of system (very basic):
 
1.7	Objectives Core & Extension
#	Objective	Type
1	Allow users (students) to input A-level subjects and predicted grades.	Core
2	Allow users to select or enter preferences: region, tuition budget, university rank preference, entrance exams.	Core
3	Store course information (course name, university, required subjects, grade requirements, fees, ranking, employability) in a database (MongoDB).	Core
4	Implement a recommendation algorithm that matches student input with courses based on subject match, grade match, and other weighted criteria.	Core
5	Display a ranked list of matching courses, with links to university pages.	Core
6	Allow sorting/filtering of results on frontend (e.g., by rank, cost, distance).	Core
7	Provide a download option (PDF or CSV) for the recommendations.	Extension
8	Include a simple login system so users can save preferences.	Extension
9	Admin interface to add/update course data.	Extension

Key Features and Technical Skills Demonstrated if successful in solution:
•	Advanced Object-Oriented Programming (OOP) using Python for backend logic.
•	Dynamic and customizable frontend UI with JSON-based layout configuration in React/Vue.js.
•	NoSQL database integration (MongoDB) allowing efficient storage and retrieval of structured and semi-structured data.
•	Implementation of advanced recommendation algorithms with weighted criteria scoring and matching.
•	Adoption of alternative structured design patterns such as Flux, Redux (for state management), or Clean Architecture for clear separation of concerns.
•	Comprehensive testing methodologies, including automated unit tests, integration tests, and usability testing. 
