import os
from flask import Flask, request, render_template, redirect, url_for
import whisper

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

model = whisper.load_model("base")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = model.transcribe(filepath, language='ru', verbose=True, word_timestamps=True)
            print("Готово")
            words_data = []
            for segment in result['segments']:
                for word_info in segment['words']:
                    word = word_info['word']
                    start = word_info['start']
                    end = word_info['end']
                    words_data.append({'word': word, 'start': start, 'end': end})
            endresult=""
            for word_data in words_data:
                print(f"[{word_data['start']} - {word_data['end']}] {word_data['word']}")
                endresult = endresult + (f"{word_data['start']} - {word_data['end']} {word_data['word']} \n ")
            print(endresult)
            time = str(result["segments"])

            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write(str(result))
                f.write(time)

            return render_template('index.html', transcript=endresult)
    return render_template('index.html', transcript=None)

if __name__ == '__main__':
    app.run(debug=True)

