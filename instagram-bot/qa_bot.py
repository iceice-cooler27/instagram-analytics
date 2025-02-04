import torch
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from better_profanity import profanity

context = '''Context::: NP-Relife-Lab programme is a student-initiated programme and workshop which aims to provide a closed-loop system solution that fosters a culture of the 3Rs (Reduce, Reuse, Recycle) to promote sustainability.
Why NP-Relife-Lab workshop?: It is to reduce the plastic waste generated from the excessive use of single-use bottles driven by convenience and a lack of awareness. To solve it, we are recycling this plastic bottles and reusing them for other purposes by molding into useful items.
Why NP-Relife-Lab Instagram account?: It is to engage students into developing sustainable habits, using various sustainability challenges daily, weekly and monthly, and also as a platform to announce workshop and event updates
Where to find the workshop, its location?: NP-Relife-Lab is located at the Atrium, Block 1 of our NP campus, right besides the cafe Sandwiches.
What is the workshop about?: Students are encourage to recycle their empty plastic bottles consumed of its contents here, which would be processed into reusable containers through a series of procedures to mold the plastic into the desired object.'''
test = "Where do I find the NP-Relife-Lab workshop?"
questions = [
    "What is the main goal of the NP-Relife-Lab programme?",
    "How does the NP-Relife-Lab workshop address plastic waste?",
    "Why was the NP-Relife-Lab Instagram account created?",
    "What types of sustainability challenges are featured on the NP-Relife-Lab Instagram account?",
    "Where is the NP-Relife-Lab workshop located on the NP campus?",
    "What can students expect to do at the NP-Relife-Lab workshop?",
    "How does the NP-Relife-Lab workshop promote the culture of the 3Rs?",
    "How are plastic bottles processed at the NP-Relife-Lab workshop?",
    "What items are made from recycled plastic bottles in the workshop?",
    "What is the purpose of recycling plastic bottles in the NP-Relife-Lab programme?"
]

# from transformers import pipeline
# question_answer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')
# result = question_answer(question=test, context=context)
# print(f"Answer: '{result['answer']}', score: {round(result['score'], 4)}, start: {result['start']}, end: {result['end']}")

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased-distilled-squad')
model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-cased-distilled-squad')

def sanitise_answer(answer):
    return profanity.censor(answer)

def get_answer(question):
    inputs = tokenizer(question, context, return_tensors="pt", padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
    print(outputs)

    start_logits = outputs.start_logits
    end_logits = outputs.end_logits

    start_index = torch.argmax(start_logits)
    end_index = torch.argmax(end_logits) + 1

    answer_tokens = inputs.input_ids[0][start_index:end_index]
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(answer_tokens))

    print("Answer:", answer)
    answer = sanitise_answer(answer)
    print("Sanitised answer:", answer)

    return answer

for question in questions:
    get_answer(question)