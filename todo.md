# Todo List for Question Paper Generator Project

## Project Overview
Develop a web application that allows users to upload a syllabus (e.g., text or file), parse it into units/topics, and generate a question paper with specified question types and counts (e.g., 20 x 1-mark, 3 x 5-mark, 5 x 8-mark questions). Integrate Google's Gemini AI to generate questions based on the uploaded syllabus and user-defined rules.

## High-Level Tasks
- [x] **Requirements Analysis** ✅
    - ✅ Define user stories (e.g., upload syllabus, select generation rules, download question paper).
    - ✅ Specify input formats (e.g., PDF, text) and output (e.g., PDF or HTML question paper).
    - ✅ Outline question generation logic (e.g., use Gemini AI for question creation from parsed units, with mark distribution and randomization).
    - See `requirements.md` for detailed documentation

- [ ] **Technology Stack Selection**
    - Choose backend (e.g., Python/FastAPI).
    - Choose frontend (e.g., React).
    - Select database (e.g., MongoDB for syllabus storage, or file-based).
    - Tools for parsing (e.g., PDF.js for uploads), generation (e.g., libraries for PDF creation), and AI integration (e.g., Google Gemini API).

- [x] **Backend Development** ✅ (MVP Complete)
    - [x] Implement syllabus upload endpoint (handle file/text input).
    - [x] Develop parsing logic to extract units/topics from syllabus.
    - [x] Integrate Google Gemini API for question generation (e.g., prompt Gemini with parsed units and rules to create questions).
    - [x] Create question generation algorithm (e.g., distribute questions across units based on rules, using Gemini for content).
    - [x] Build API for generating and serving question papers.
    - [ ] Add authentication if needed (e.g., user accounts) - Future enhancement.

- [ ] **Frontend Development**
    - [ ] Design UI for syllabus upload.
    - [ ] Create interface for configuring question rules (e.g., number of 1-mark, 5-mark questions).
    - [ ] Implement preview/download of generated question paper.
    - [ ] Ensure responsive design.

- [ ] **Database/Modeling**
    - [ ] Design schema for storing syllabi, units, and generated questions.
    - [ ] Implement CRUD operations for syllabus management.

- [ ] **Integration and Logic**
    - [ ] Integrate parsing with Gemini generation (e.g., map questions to units).
    - [ ] Handle edge cases (e.g., insufficient topics, custom rules, API rate limits).
    - [ ] Add randomization for question selection via Gemini prompts.

- [ ] **Testing**
    - [ ] Unit tests for parsing and generation logic, including Gemini API calls.
    - [ ] Integration tests for full upload-to-generate flow.
    - [ ] User acceptance testing with sample syllabi.

- [ ] **Deployment and Maintenance**
    - [ ] Set up hosting (e.g., Heroku, AWS).
    - [ ] Implement error handling and logging, including API failures.
    - [ ] Add documentation and user guide.
    - [ ] Plan for updates (e.g., adding more question types or AI models).

## Milestones
- [ ] MVP: Basic upload, parse 5 units, generate fixed question set using Gemini.
- [ ] Full Release: Custom rules, multiple formats, user accounts, advanced Gemini prompts.