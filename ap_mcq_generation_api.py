from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from openai import OpenAI

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

OPENAI_API_KEY = ""
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def call_openai_api(messages: List[Dict[str, str]]) -> str:
    """Make API call to OpenAI"""
    try:
        response = openai_client.chat.completions.create(
            model="o3-mini",
            messages=messages,
            reasoning_effort="high"
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, 
                          detail=f"Error calling OpenAI API: {str(e)}")

# Prompts and constants (to be filled)

# Constants



absolutes = """all, absolute, always, complete, completely, entirely, every, exclusively, extinction, identical,
immediate, immediately, irrelevant, never, none, purely, solely, sole,unchanging, uniform, universal"""

blooms_easy = """
"Of the following, which definition" Define: Provide the exact meaning of a word, term, or concept. To use in multiple choice:
"Select the statement which best identifies" Identify: Recognize and name specific components or characteristics.
"Which list" List: Enumerate items or ideas in a concise format.
"Which response best states" State: Express information clearly and concisely.
"Choose the option that best describes" Describe: Provide a detailed account of something's characteristics or features.
"Select the best explanation" Explain: Clarify a concept or process by providing reasons or examples.
"Choose the best summary" Summarize: Present the main points of information in a concise form.
"What interpretation" Interpret: Explain the meaning or significance of something.
"Which statement best illustrates" Illustrate: Provide examples or visual representations to clarify a point.
"How should one classify" Classify: Organize items into categories based on shared characteristics.
"Select the statement that best compares" Compare: Examine similarities between two or more things.
"Which statement best shows the contrast" Contrast: Examine differences between two or more things.
"How should you classify" Categorize: Group items or concepts based on shared characteristics.
"From the following options, choose the best estimate" Estimate: Make an approximate calculation or judgment.
"Which prediction" Predict: Anticipate future outcomes based on current information.
"""

# bloom_moderate: Bloom's (Applying, Analyzing), DOK (3) Task verbs:
blooms_moderate = """
Calculate: Determine a value using mathematical processes.
"Which statement demonstrates" Demonstrate: Show how something works or how a process is completed.
"Determine which option" Determine: Establish or conclude after consideration or investigation.
"Choose the best option from the following options to respond to the question. Differentiate.." Differentiate: Identify the differences between two or more things.
"Which response best justifies" Justify: Provide reasons or evidence to support a claim or decision.
Organize: Arrange information or items in a structured manner.
"Which response best relates" Relate: Show or establish a connection between things.
Solve: Find a solution to a problem or challenge.
"Which statement best supports" Support: Provide evidence or arguments to back up a claim or position.
"""

# bloom_difficult: Bloom's (Evaluating, Creating), DOK (4) Task verbs:
blooms_difficult = """
"Of the following responses, which is the most accurate appraisal" Appraise: Assess the value or quality of something.
"Apply what you learned in the article to" Apply: Use knowledge or skills in a new situation.
"Which argument best" Argue: Present reasons for or against a point or idea.
"Which is the most logical conclusion..." Conclude: Reach a logical end or judgment by reasoning.
"What is the most likely critique for" Critique: Offer a detailed analysis and assessment of something.
"Which of the following is the best design for" Design: Plan or create something for a specific purpose.
"What is the most logical evaluation" Evaluate: Make a judgment about the value or quality of something.
"Which hypothesis" Hypothesize: Propose an explanation for a phenomenon based on limited evidence.
Judge: Form an opinion or conclusion about something.
"Which is the most logical plan" Plan: Devise a method for doing or achieving something.
"Which of the following would you propose as the best" Propose: Put forward an idea or plan for consideration.
"Which of the following would you recommend  " Recommend: Suggest something as worthy of being adopted or done.
"""

qcriteria = """
Relates to one or more ek_codes
Contains task verbs from LOs if present
Can be answered by information in the text.
Can be answered in 1 to 2 short sentences
Connects a concept in the text to the broader themes in the ek or lo codes
The question contains all of the information a well prepared student would need to find the correct response.
The question is clearly stated (does not have another interpretation)
There is only one connection being made in the question: the word and is not used to create compound questions
"""

correct_criteria = """
The response is factually correct
Is one sentence of up to 20 words.
Responds to all parts of the question. If the question asks for a comparison, a comparison is made.
Correctly uses the task verb. If the question is regarding an argument, the response includes an argument. If the question asks for a combination, the response includes a combination
"""

distractor_criteria = """
A distractor does not use {ABSOLUTES} or extreme phrases because an intelligent student would not believe sentences with these words
Is not more than 2 words longer or shorter than the correct response.
Contains the same number of commas as the correct response
Correctly uses the task verbs in blooms. If the question is regarding an argument, the response includes an argument. If the question asks for a combination, the response includes a combination
Responds to all parts of the question
Could not be confused for a correct answer
Each distractor is unique in interpretation from all other response options
Is related to the time period or lo_code
"""

explanation_criteria = """
Factually correct information provided to enhance or cement student learning
1-2 sentences explaining: why the response is correct or incorrect based on relevant information in the text.
Addresses what is correct and what is incorrect in the response
"""

# JSON structure variables
question_json_structure = '''{
  "questions": [
    {
      "question_number": 1,
      "question_text": "string",
      "ek_code_specific_to_this_question": "string",
      "lo_code_specific_to_this_question": "string",
      "task_verb": "string",
      "difficulty": "integer"
    },
    {
      "question_number": 2,
      "question_text": "string",
      "ek_code_specific_to_this_question": "string",
      "lo_code_specific_to_this_question": "string",
      "task_verb": "string",
      "difficulty": "integer"
    },
    {
      "question_number": 3,
      "question_text": "string",
      "ek_code_specific_to_this_question": "string",
      "lo_code_specific_to_this_question": "string",
      "task_verb": "string",
      "difficulty": "integer"
    }
  ]
}'''

correct_answer_json_structure = '''{
  "correct_answer": {
    "response_text": "string"
  }
}'''

distractor_json_structure = '''{
  "distractors": {
    "d1": { "response_text": "string" },
    "d2": { "response_text": "string" },
    "d3": { "response_text": "string" }
  }
}'''

explanation_json_structure = '''{
  "explanations": {
    "correct_answer_explanation": "string",
    "distractor_explanations": {
      "d1": { "explanation": "string" },
      "d2": { "explanation": "string" },
      "d3": { "explanation": "string" }
    }
  }
}'''

# Pydantic models for request/response validation
class QuestionRequest(BaseModel):
    article: str
    current_question_bank: str
    ek_codes: str
    lo_codes: str

class Question(BaseModel):
    question_number: int
    question_text: str
    ek_code_specific_to_this_question: str
    lo_code_specific_to_this_question: str
    task_verb: str
    difficulty: int

class QuestionsResponse(BaseModel):
    questions: List[Question]

class CorrectAnswer(BaseModel):
    response_text: str

class CorrectAnswerResponse(BaseModel):
    correct_answer: CorrectAnswer

class DistractorResponse(BaseModel):
    response_text: str

class Distractors(BaseModel):
    d1: DistractorResponse
    d2: DistractorResponse
    d3: DistractorResponse

class DistractorsResponse(BaseModel):
    distractors: Distractors

class DistractorExplanation(BaseModel):
    explanation: str

class DistractorExplanations(BaseModel):
    d1: DistractorExplanation
    d2: DistractorExplanation
    d3: DistractorExplanation

class Explanations(BaseModel):
    correct_answer_explanation: str
    distractor_explanations: DistractorExplanations

class ExplanationsResponse(BaseModel):
    explanations: Explanations

class MCQResponse(BaseModel):
    label: str
    isCorrect: bool
    explanation: str

class MCQuestion(BaseModel):
    material: str
    responses: List[MCQResponse]
    difficulty: int

class QuestionBankResponse(BaseModel):
    questionBank: List[MCQuestion]



def generate_question_set(difficulty: int, blooms: str, 
                         request_data: QuestionRequest) -> List[Question]:
    """Generate questions for a specific difficulty level"""
    prompt = f"""You are a psychometrician turned high school teacher. Your task is building AP level learning assessments.
The assessment is to test whether students read this <article>{request_data.article}</article>
+Use task verbs from <blooms>{blooms}</blooms> to write exactly three questions that will prove a student can connect the article information to their understanding
+Read these <questions>{request_data.current_question_bank}</questions> that are already on the assessment to ensure you do not write a duplicate question.
+Follow these specific <criteria>{qcriteria}</criteria>
+You must write all 3 questions without using and to create compund questions.
+Ask the 3 questions in the format "which" "what" "how" "why"  etc
+For each question, specify which ek_code and lo_code it addresses from <ek>{request_data.ek_codes}</ek> and <lo>{request_data.lo_codes}</lo>
+Do not refer to the article in the question. students know where the questions come from.
+All questions in this set should have difficulty: {difficulty}
You have to cleverly add escape characters if something could break the JSON from being processed through code. You have to strictly use the provided schema.

Please output your response in this exact JSON format without any additional text outside JSON:
{question_json_structure}"""
    response = call_openai_api([{"role": "user", "content": prompt}])
    
    questions_json = json.loads(response)
    return QuestionsResponse(**questions_json).questions

def generate_correct_answer(question: Question, 
                          request_data: QuestionRequest) -> str:
    """Generate correct answer for a single question"""
    blooms = blooms_easy if question.difficulty == 1 else (
        blooms_moderate if question.difficulty == 2 else blooms_difficult)
    
    prompt = f"""You are a student who has to take an AP assessment.
The teacher wants to be sure you read <article>{request_data.article}</article>, and that you understand how to connect <ek>{request_data.ek_codes}</ek> and other information in the article to the important <lo>{request_data.lo_codes}</lo> and has written an assignment.
This is the question <question>{question.question_text}</question>.
+You must first identify the task verb used in the question. Review Blooms <difficulty>{blooms}</difficulty> to ensure that you correctly follow the necessary steps to answer the question.
-(e.g. if the question asks for a definition, you will provide a definition in the correct response)
+The teacher also gave you <criteria>{correct_criteria}</criteria> to teach you how to answer these questions and do well on the AP Exam.
+You must answer this question correctly in only 1 sentence of less than 20 words.
+You have to use information found in the article along with your existing knowledge of the topic
+Do not restate the question in your response.
+You must answer this question correctly in only 1 sentence of less than 20 words.
Please make sure you strictly follow the JSON schema and write the correct answer.
+The response must be factually correct
You have to cleverly add escape characters if something could break the JSON from being processed through code. You have to strictly use the provided schema.

Please output your response in this exact JSON format without any additional text outside JSON:
{correct_answer_json_structure}"""
    response = call_openai_api([{"role": "user", "content": prompt}])
    
    correct_json = json.loads(response)
    return CorrectAnswerResponse(**correct_json).correct_answer.response_text

def generate_distractors(question: Question, correct_answer: str, 
                        request_data: QuestionRequest) -> Distractors:
    """Generate distractors for a single question"""
    blooms = blooms_easy if question.difficulty == 1 else (
        blooms_moderate if question.difficulty == 2 else blooms_difficult)
    
    prompt = f"""You are a psychometrician turned high school teacher. Your task is building assessments for AP level learning assessments.
The assessment is to test whether students read this <article>{request_data.article}</article>
The <question>{question.question_text}</question> and the <correct>{correct_answer}</correct> are already written.
A distractor is a believable lie that a teacher might tell to determine whether a student read the article before the exam.
Now you must devise exactly three plausible distractors to the question that will trick students who came to class but did not read the article well.
+Even though a response is incorrect, it must address all parts of the question.
You must first identify the task verb used in the question. Review Blooms <blooms>{blooms}</blooms> to ensure that you understand the taskverbs and do what the question is asking.
+You have to use information found in the article along with your existing knowledge about the topic
+Distractors must be very similar to the correct response. Review the <criteria>{distractor_criteria}</criteria>
+Do not restate the question in your response.
Please make sure you strictly follow the JSON schema and write the distractors.
+You must write the distractors for this question in only 1 sentence of less than 20 words each.
+You must write all 3 distractors.
You have to cleverly add escape characters if something could break the JSON from being processed through code. You have to strictly use the provided schema.

Please output your response in this exact JSON format without any additional text outside JSON:
{distractor_json_structure}"""
    response = call_openai_api([{"role": "user", "content": prompt}])
    
    distractors_json = json.loads(response)
    return DistractorsResponse(**distractors_json).distractors

def generate_explanations(question: Question, correct_answer: str, 
                         distractors: Distractors, 
                         request_data: QuestionRequest) -> Explanations:
    """Generate explanations for a single question"""
    prompt = f"""You are a psychometrician turned high school teacher. Your task is writing feedback for the students in your class.
The assessment is to test whether students read this <article>{request_data.article}</article>
+See the <question>{question.question_text}</question> and guidelines for feedback <criteria>{explanation_criteria}</criteria>
+One student wrote a <correct>{correct_answer}</correct> using the information from the article, follow the criteria to explain in 1-2 sentences why this information is correct to solidify their learning
+Three students wrote incorrect responses <distractors>{distractors}</distractors>. using the information from the article, follow the criteria to explain in 1-2 sentences why this information is wrong to strengthen their understanding
 using the information from the article, your own knowledge of the topic and the images, follow the criteria to explain in 1-2 sentences why this information is wrong to strengthen their understanding
         +Rather than referring to the article, start each explanation with "This answer is correct/incorrect. You previously learned" followed by the correct information that would help answer the question
          +If the information is not directly in the article, explain how the student could apply critical thinking to arrive at the correct response.
         +DO NOT REFER TO THE ARTICLE OR THE READING MATERIAL directly. You have to use that along with your own knowledge to write high quality explanations.
        +You must write explanations for the correct answer and all distractors using both the article and relevant images. If the information in the article is not sufficient, then you can use your own knowledge to write the explanations.
        You have already been provided with the correct and the incorrect responses you have to write the explanations based on that information.
        You have to cleverly add escape characters if something could break the JSON from being processed through code.
Please output your response in this exact JSON format without any additional text outside JSON:
{explanation_json_structure}"""
    response = call_openai_api([{"role": "user", "content": prompt}])
    
    explanations_json = json.loads(response)
    return ExplanationsResponse(**explanations_json).explanations

def format_mcq(question: Question, correct_answer: str, 
               distractors: Distractors, 
               explanations: Explanations) -> MCQuestion:
    """Format a single MCQ with randomized correct answer position"""
    options = [
        MCQResponse(
            label=correct_answer,
            isCorrect=True,
            explanation=explanations.correct_answer_explanation
        ),
        MCQResponse(
            label=distractors.d1.response_text,
            isCorrect=False,
            explanation=explanations.distractor_explanations.d1.explanation
        ),
        MCQResponse(
            label=distractors.d2.response_text,
            isCorrect=False,
            explanation=explanations.distractor_explanations.d2.explanation
        ),
        MCQResponse(
            label=distractors.d3.response_text,
            isCorrect=False,
            explanation=explanations.distractor_explanations.d3.explanation
        )
    ]
    
    random.shuffle(options)
    
    return MCQuestion(
        material=question.question_text,
        responses=options,
        difficulty=question.difficulty
    )

def update_question_numbers(questions: List[Question], difficulty: int) -> List[Question]:
    """Update question numbers based on difficulty level"""
    offset = (difficulty - 1) * 3  # 0 for diff 1, 3 for diff 2, 6 for diff 3
    updated_questions = []
    for i, q in enumerate(questions, 1):
        q_dict = q.dict()
        q_dict['question_number'] = offset + i
        updated_questions.append(Question(**q_dict))
    return updated_questions

@app.post("/generate-questions", response_model=QuestionBankResponse)
def generate_question_bank(request: QuestionRequest):
    """Main API endpoint to generate question bank"""
    try:
        all_questions = []
        
        # Generate questions for all difficulty levels in parallel
        difficulties = [
            (1, blooms_easy),
            (2, blooms_moderate),
            (3, blooms_difficult)
        ]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_diff = {
                executor.submit(generate_question_set, diff, blooms, request): (diff, blooms) 
                for diff, blooms in difficulties
            }
            
            # Process each difficulty level's questions
            difficulty_questions = {}
            for future in as_completed(future_to_diff):
                diff, _ = future_to_diff[future]
                questions = future.result()
                # Update question numbers based on difficulty level
                updated_questions = update_question_numbers(questions, diff)
                difficulty_questions[diff] = updated_questions

            # Combine questions in order of difficulty
            for diff in sorted(difficulty_questions.keys()):
                all_questions.extend(difficulty_questions[diff])

        # Verify we have 9 questions
        if len(all_questions) != 9:
            raise HTTPException(
                status_code=500,
                detail=f"Expected 9 questions but got {len(all_questions)}"
            )

        # Create a mapping of question numbers to questions for easy lookup
        question_map = {q.question_number: q for q in all_questions}
        
        # Generate correct answers in parallel
        correct_answers = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_question_num = {
                executor.submit(generate_correct_answer, q, request): q.question_number 
                for q in all_questions
            }
            
            for future in as_completed(future_to_question_num):
                question_num = future_to_question_num[future]
                try:
                    correct_answers[question_num] = future.result()
                except Exception as e:
                    print(f"Error generating correct answer for question {question_num}: {str(e)}")
                    raise
        
        # Generate distractors in parallel
        distractors = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_question_num = {
                executor.submit(
                    generate_distractors,
                    question_map[q_num],
                    correct_answers[q_num],
                    request
                ): q_num 
                for q_num in correct_answers.keys()
            }
            
            for future in as_completed(future_to_question_num):
                question_num = future_to_question_num[future]
                try:
                    distractors[question_num] = future.result()
                except Exception as e:
                    print(f"Error generating distractors for question {question_num}: {str(e)}")
                    raise
        
        # Generate explanations in parallel
        explanations = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_question_num = {
                executor.submit(
                    generate_explanations,
                    question_map[q_num],
                    correct_answers[q_num],
                    distractors[q_num],
                    request
                ): q_num for q_num in distractors.keys()
            }
            
            for future in as_completed(future_to_question_num):
                question_num = future_to_question_num[future]
                try:
                    explanations[question_num] = future.result()
                except Exception as e:
                    print(f"Error generating explanations for question {question_num}: {str(e)}")
                    raise
        
        # Format all MCQs
        question_bank = []
        for q_num in sorted(question_map.keys()):  # Sort by question number
            try:
                mcq = format_mcq(
                    question=question_map[q_num],
                    correct_answer=correct_answers[q_num],
                    distractors=distractors[q_num],
                    explanations=explanations[q_num]
                )
                question_bank.append(mcq)
            except Exception as e:
                print(f"Error formatting MCQ for question {q_num}: {str(e)}")
                raise

        # Verify final question bank has 9 questions
        if len(question_bank) != 9:
            raise HTTPException(
                status_code=500,
                detail=f"Final question bank has {len(question_bank)} questions instead of 9"
            )
        
        return QuestionBankResponse(questionBank=question_bank)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
