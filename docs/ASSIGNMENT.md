# Slide Generator API

## Objective

Create a backend application that generates customizable presentation slides on any topic using Python.

---

## Requirements

### Core Features

#### Content Generation API

- Accept topic/subject as input.
- Generate relevant content using LLMs (Large Language Models).
- Support custom content input.
- Include image suggestions (optional).

#### Slide Configuration

- Number of slides (min 1, max 20).
- Support for 4 slide layouts:
  - Title slide
  - Bullet points (3–5 points)
  - Two-column layout
  - Content with image placeholder
- Apply a consistent theme/styling.
- Support custom fonts and colors.

#### Citation & References

- Include source citations in the slides.

#### Export Functionality

- Generate PowerPoint (`.pptx`) files.

---

## Technical Requirements

### P0 Deliverable

Implement the following RESTful endpoints:

#### API Endpoints

- `POST   /api/v1/presentations`  
  Create a new presentation

- `GET    /api/v1/presentations/{id}`  
  Retrieve presentation details

- `GET    /api/v1/presentations/{id}/download`  
  Download presentation as PPTX

- `POST   /api/v1/presentations/{id}/configure`  
  Modify presentation configuration

### Slide Generation

- Use `python-pptx` or an equivalent library.

---

## Stretch Deliverables

### API Enhancements

- Request/response validation
- Error handling
- Rate limiting
- Authentication (optional)

### Templating and Advanced Features

- Implement a templating system
- Support concurrent requests
- Handle different aspect ratios

### Stretch Goal: Performance

- Optimize content generation
- Implement caching
- Handle multiple simultaneous requests efficiently

---

## Deliverables

- ✅ Source code with documentation
- ✅ API documentation
- ✅ Setup instructions
- ✅ 3 sample presentations (`.pptx` files)

---

## Evaluation Criteria

- Code quality and organization
- Performance optimization
- Documentation (clarity, completeness, ease of use)

---

## Time Allocation

Estimated effort: **4–6 hours**

---

## Submission

Please provide a private GitHub repository link containing:

- Source code
- `README.md` (this file)
- `requirements.txt` (listing all dependencies)
- Sample output presentations (`.pptx`) in a designated folder
