import os
import speech_recognition as sr
# from pydub import AudioSegment as am






# def downgrade_sample_rate(filename):
#     sound = am.from_file(filename, format="wav", frame_rate=22050)
#     sound = sound.set_frame_rate(41000)
#     sound.export(filename, format="wav")


def speech_to_text(audio):
    # if not os.path.exists('audio'):
    #     os.mkdir('audio')

    # if os.path.exists("audio/tmp_audio_0.wav"):
    #     i = 0
    #     while True:
    #         if os.path.exists(f"audio/tmp_audio_{i}.wav"):
    #             i += 1
    #         else:
    #             filename = f"audio/tmp_audio_{i}.wav"
    #             break
    # else:
    #     filename = "audio/tmp_audio_0.wav"

    # with open(filename, "wb") as file:
    #     file.write(audio.get_wav_data())

    # downgrade_sample_rate(filename)

    try:
        r = sr.Recognizer()
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "ERROR: Couldn't understand."
    except sr.RequestError as e:
        return "ERROR: Could not request results from Wit.ai service; {0}".format(e)

