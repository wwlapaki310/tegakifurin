from flask import Flask
from flask import render_template
from flask import request
from PIL import Image
from PIL import ImageDraw, ImageFont
from collections import namedtuple
import cv2
import math
from requests_oauthlib import OAuth1Session
import json

app = Flask(__name__)

# テキスト関連のデータまとめ用のタプル
Cc = namedtuple("Cc", [
    "start_index",
    "stop_index",
    "text",
    "font",
    "rgba",
    "point"
])


def get_fps_n_count(video_path):
    """動画のfpsとフレーム数を返す"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return (None, None)

    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = round(cap.get(cv2.CAP_PROP_FPS))

    cap.release()
    #cv2.destroyAllWindows()
    return (fps, count)


def aspect_ratio(width, height):
    """アスペクト比を返す"""
    gcd = math.gcd(width, height)
    ratio_w = width // gcd
    ratio_h = height // gcd
    return (ratio_w, ratio_h)


def resize_based_on_aspect_ratio(aspect_ratio, base_width, max_width=400):
    """アスペクト比を元にリサイズ後のwidth, heightを求める"""
    if base_width < max_width:
        return None

    base = max_width / aspect_ratio[0]
    new_w = int(base * aspect_ratio[0])
    new_h = int(base * aspect_ratio[1])
    return (new_w, new_h)


def get_frame_range(video_path, start_frame, stop_frame, step_frame):
    """指定された範囲の画像をPillowのimage objectのリストにする"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    asp = aspect_ratio(width, height)
    # でかすぎてもあれなので最大幅を400にしとく
    width_height = resize_based_on_aspect_ratio(asp, width, max_width=400)

    im_list = []
    for n in range(start_frame, stop_frame, step_frame):
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = cap.read()
        if ret:
            if width_height is not None:
                frame = cv2.resize(frame, dsize=width_height)
            # BGRをRGBにする
            img_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # numpyのarrayからPillowのimage objectを作る
            im = Image.fromarray(img_array)
            im_list.append(im)

    cap.release()
    #cv2.destroyAllWindows()
    return im_list


def make_gif(filename, im_list):
    """gifを作る"""
    im_list[0].save(filename, save_all=True, append_images=im_list[1:], loop=0)

def make_cc(gif_fps, start_sec, stop_sec, text, font, rgba, point):
    start_index = start_sec * gif_fps
    stop_index = stop_sec * gif_fps
    return Cc(start_index, stop_index, text, font, rgba, point)


def add_text_to_image(im_list, cc_list):   
    new_im_list = []
    for index, im_obj in enumerate(im_list):
        new_im = None
        for cc in cc_list:
            if index >= cc.start_index and index <= cc.stop_index:
                if new_im is None:
                    new_im = add_text_to_image_object(im_obj, cc)
                else:
                    new_im = add_text_to_image_object(new_im, cc)

        if new_im is None:
            new_im_list.append(im_obj)
        else:
            new_im_list.append(new_im)

    return new_im_list


def add_text_to_image_object(im_obj, cc):
    base = im_obj.convert('RGBA')
    # make a blank image for the text, initialized to transparent text color
    text_img = Image.new('RGBA', base.size, (255,255,255,0))

    # get a drawing context
    d = ImageDraw.Draw(text_img)

    # draw text
    d.text(cc.point, cc.text, font=cc.font, fill=cc.rgba)

    out = Image.alpha_composite(base, text_img)
    return out
 
@app.route('/', methods = ["GET" , "POST"])
def index():
    if request.method == 'POST':
        inputmozi= request.form['inputmozi']
        print(inputmozi)
        count=len(inputmozi)
        print(count)
        if(count==5):
            video_file5 = "5mozi.mp4"
            text5=inputmozi
            fps, count = get_fps_n_count(video_file5)
            if fps is None:
                print("動画ファイルを開けませんでした")
            # gifにしたい範囲を指定
            start_sec = 0
            stop_sec = 8
            start_frame = int(start_sec * fps)
            stop_frame = int(stop_sec * fps)
            step_frame = 3
            print("開始(けっこう時間がかかる5)")
            im_list = get_frame_range(video_file5, start_frame, stop_frame, step_frame)
            if im_list is None:
                print("動画ファイルを開けませんでした") 
            # テキスト関連の処理
            gif_fps = len(im_list) // (stop_sec - start_sec)
            font1 = ImageFont.truetype(font="meiryo.ttc", size=60)
            cc1 = make_cc(gif_fps, 2, 8, text5[0], font1, (255, 0, 0, 255), (25, 70))
            cc2 = make_cc(gif_fps, 3, 8, text5[1], font1, (255, 0, 0, 255), (85, 70))
            cc3 = make_cc(gif_fps, 4, 8, text5[2], font1, (255, 0, 0, 255), (145, 70))
            cc4 = make_cc(gif_fps, 5, 8, text5[3], font1, (255, 0, 0, 255), (205, 70))
            cc5 = make_cc(gif_fps, 6, 8, text5[4], font1, (255, 0, 0, 255), (265, 70))
            new_im_list = add_text_to_image(im_list, [cc1, cc2, cc3, cc4,cc5])
            url='static/'+text5+'.gif'
            print(url)
            make_gif('static/'+text5+'.gif', new_im_list)
            return render_template('result.html',inputmozi=inputmozi,count=5,url=url)

        elif(count==10):
            video_file10 = "10mozi.mp4"
            text10=inputmozi
            fps, count = get_fps_n_count(video_file10)
            if fps is None:
                print("動画ファイルを開けませんでした")
                # gifにしたい範囲を指定
            start_sec = 0
            stop_sec = 12
            start_frame = int(start_sec * fps)
            stop_frame = int(stop_sec * fps)
            step_frame = 3
            print("開始(けっこう時間がかかる10)")
            im_list = get_frame_range(video_file10, start_frame, stop_frame, step_frame)
            if im_list is None:
                print("動画ファイルを開けませんでした") 
            # テキスト関連の処理
            gif_fps = len(im_list) // (stop_sec - start_sec)
            font1 = ImageFont.truetype(font="meiryo.ttc", size=60)
            cc1 = make_cc(gif_fps, 2, 12, text10[0], font1, (255, 0, 0, 255), (25, 40))
            cc2 = make_cc(gif_fps, 3.2, 12, text10[1], font1, (255, 0, 0, 255), (85, 40))
            cc3 = make_cc(gif_fps, 4, 12, text10[2], font1, (255, 0, 0, 255), (145, 40))
            cc4 = make_cc(gif_fps, 5, 12, text10[3], font1, (255, 0, 0, 255), (205, 40))
            cc5 = make_cc(gif_fps, 6, 12, text10[4], font1, (255, 0, 0, 255), (265, 40))
            cc6 = make_cc(gif_fps, 7, 12, text10[5], font1, (255, 0, 0, 255), (25, 100))
            cc7 = make_cc(gif_fps, 7.5, 12, text10[6], font1, (255, 0, 0, 255), (85, 100))
            cc8 = make_cc(gif_fps, 8, 12, text10[7], font1, (255, 0, 0, 255), (145, 100))
            cc9 = make_cc(gif_fps, 9, 12, text10[8], font1, (255, 0, 0, 255), (205, 100))
            cc10 = make_cc(gif_fps, 10, 12, text10[9], font1, (255, 0, 0, 255), (265, 100))
            new_im_list = add_text_to_image(im_list, [cc1, cc2, cc3, cc4,cc5,cc6,cc7,cc8,cc9,cc10])
            url='static/'+text10+'.gif'
            print(url)
            make_gif(url, new_im_list)
            return render_template('result.html',inputmozi=inputmozi,count=10,url=url)

    else:
        return render_template('index.html',message='Hello')

@app.route('/result', methods = ["GET" , "POST"])
def result():
    return render_template("result.html")


if __name__ == "__main__":
    app.run()