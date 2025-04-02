# AP MCQ Generator API

Hosted at https://api-mcq-generation.onrender.com

## Overview
An API that automatically generates AP Biology multiple-choice questions based on provided article content. The system generates a comprehensive set of 18 questions across three difficulty levels, complete with correct answers, distractors, and explanations.

## Features
- Generates 18 high-quality MCQs (6 each at three difficulty levels)
- Questions aligned with AP Biology EK and LO codes
- Each question includes:
  - Question text
  - 4 response options (1 correct, 3 distractors)
  - Detailed explanations for all options
  - Difficulty level
- Randomized correct answer positions
- Parallel processing for faster generation
- Input validation using Pydantic
- CORS enabled for web integration

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/ap-mcq-generator.git
cd ap-mcq-generator
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional)
```bash
export OPENAI_API_KEY="your-api-key"
```

## Usage

### Running the API Server
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

### Using the HTML Interface
1. Open `index.html` in a web browser
2. Fill in the required fields:
   - Article text
   - Current question bank (to avoid duplicates)
   - EK codes
   - LO codes
3. Click "Generate Questions"
4. View the generated questions in formatted JSON

## API Documentation

### Generate Questions Endpoint

#### Request
```
POST /generate-questions
```

##### Request Body Schema
```json
{
    "article": "string",
    "current_question_bank": "string",
    "ek_codes": "string",
    "lo_codes": "string"
}
```

##### Example Request
```python
import requests

data = {
    "article": "Recent studies in cellular biology have shown...",
    "current_question_bank": "Previous question set...",
    "ek_codes": "EK-1.A, EK-1.B",
    "lo_codes": "LO-1.1, LO-1.2"
}

response = requests.post(
    "http://localhost:8000/generate-questions",
    json=data
)
```

#### Response
```json
{
    "questionBank": [
        {
            "material": "What is the primary function of...",
            "responses": [
                {
                    "label": "It facilitates the transport of...",
                    "isCorrect": true,
                    "explanation": "This is correct because..."
                },
                {
                    "label": "It produces energy through...",
                    "isCorrect": false,
                    "explanation": "This is incorrect because..."
                }
            ],
            "difficulty": 1
        }
    ]
}
```

## Question Types and Difficulty Levels

### Easy Questions (Difficulty 1)
- Focus on remembering and understanding
- Use verbs like: Define, Identify, List, State, Describe
- 6 questions generated

### Medium Questions (Difficulty 2)
- Focus on applying and analyzing
- Use verbs like: Analyze, Calculate, Demonstrate, Determine
- 6 questions generated

### Hard Questions (Difficulty 3)
- Focus on evaluating and creating
- Use verbs like: Evaluate, Create, Design, Hypothesize
- 6 questions generated

## Error Handling

### Common Error Responses
- `400 Bad Request`: Missing or invalid input parameters
- `500 Internal Server Error`: Server-side error or AI service error

### Example Error Response
```json
{
    "detail": "Error message describing the issue"
}
```

## Development

### Project Structure
```
ap-mcq-generator/
├── ap_mcq_geneation_api.py           # FastAPI application
├── requirements.txt  # Project dependencies
└── README.md        # Documentation
```

### Dependencies
- FastAPI: Web framework
- Pydantic: Data validation
- Anthropic Claude API: Question generation
- concurrent.futures: Parallel processing

### Local Development
1. Start the server with auto-reload:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
```
http://localhost:8000/docs
```

## Best Practices
1. Provide clear, focused article content
2. Include specific EK and LO codes
3. Maintain a comprehensive question bank to avoid duplicates
4. Allow sufficient time for question generation
5. Monitor API response times and errors

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
