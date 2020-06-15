import os
import cv2
import wx
from pose import run_video,count_jumpup,count_situp,count_squat
from modules.inference_engine import InferenceEngine
from modules.input_reader import InputReader
from modules.draw import draw_poses
from modules.parse_poses import parse_poses

# home page structure
class homePage(wx.App):
    def __init__(self):
        wx.App.__init__(self)

        self.frame = wx.Frame(None, title='Home Page', size = (640, 360))
        self.frame.SetBackgroundColour("WHITE")

        # NO IDEA icon
        no_idea_icon = wx.Image("icon/noidea.png", wx.BITMAP_TYPE_ANY)
        no_idea_icon = no_idea_icon.Scale(70, 70, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        no_idea_icon = wx.StaticBitmap(self.frame, -1, no_idea_icon, (0,250))

        # Fit At Home label
        home_label = wx.StaticText(self.frame, -1, label = "Fit At Home", pos = wx.Point(430, 10), style = wx.ALIGN_RIGHT)
        home_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 
        home_label.SetForegroundColour((234,152,153))
        home_label.SetFont(home_font)

        # Video Button        
        video_icon = wx.Image("icon/video.jpg", wx.BITMAP_TYPE_ANY)
        video_icon = video_icon.Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        video_Btn = wx.BitmapButton(self.frame, -1, video_icon, pos=(150,100))
        video_Btn.Bind(wx.EVT_BUTTON, self.videoOnBtn)

        
        # Webcam Button
        webcam_icon = wx.Image("icon/webcam.jpg", wx.BITMAP_TYPE_ANY)
        webcam_icon= webcam_icon.Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        webcam_Btn = wx.BitmapButton(self.frame, -1, webcam_icon, pos=(350,100))
        webcam_Btn.Bind(wx.EVT_BUTTON, self.webcamoOnBtn)

        self.frame.Show()
    
    def videoOnBtn(self, event):
        videoPage = VideoPage("Video")
        wx.CallAfter(self.frame.Close)
        videoPage.MainLoop()

    def webcamoOnBtn(self, event):
        videoPage = VideoPage("Webcam")
        wx.CallAfter(self.frame.Close)
        videoPage.MainLoop()

# choose video page 
class VideoPage(wx.App):
    def __init__(self, input_type):
        wx.App.__init__(self, input_type)

        self.frame = wx.Frame(None, title=input_type, size = (640, 360))
        self.frame.SetBackgroundColour("WHITE")
        
        # Store video path
        self.video_path = None

        # Store the category of action(sit up, squat, junpingjack)
        self.state = "situp"
        self.input_type = input_type

        # NO IDEA icon
        no_idea_icon = wx.Image("icon/noidea.png", wx.BITMAP_TYPE_ANY)
        no_idea_icon = no_idea_icon.Scale(70, 70, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        no_idea_icon = wx.StaticBitmap(self.frame, -1, no_idea_icon, (0,250))

        # input type label
        if(input_type == "Video"):
            video_label = wx.StaticText(self.frame, -1, label = input_type, pos = wx.Point(520,10), style = wx.ALIGN_RIGHT)
        elif(input_type == "Webcam"):
            video_label = wx.StaticText(self.frame, -1, label = input_type, pos = wx.Point(480,10), style = wx.ALIGN_RIGHT)

        video_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 
        video_label.SetForegroundColour((234,152,153))
        video_label.SetFont(video_font)

        label_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 

        # Sit up Button
        situp_label = wx.StaticText(self.frame, -1, label="Sit-up", pos=(105,65), style= wx.ALIGN_RIGHT)
        situp_label.SetForegroundColour((89,89,89))
        situp_label.SetFont(label_font)

        situp_icon = wx.Image("icon/situp.jpg", wx.BITMAP_TYPE_ANY)
        situp_icon = situp_icon.Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        self.situp_Btn = wx.BitmapButton(self.frame, -1, situp_icon, pos=(70,90))
        self.situp_Btn.Bind(wx.EVT_BUTTON, self.situpOnBtn)

        # Squat Button
        squat_label = wx.StaticText(self.frame, -1, label="Squat", pos=(280,65), style= wx.ALIGN_RIGHT)
        squat_label.SetForegroundColour((89,89,89))
        squat_label.SetFont(label_font)

        squat_icon = wx.Image("icon/squat.jpg", wx.BITMAP_TYPE_ANY)
        squat_icon = squat_icon.Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        squat_Btn = wx.BitmapButton(self.frame, -1, squat_icon, pos=(245,90))
        squat_Btn.Bind(wx.EVT_BUTTON, self.squatOnBtn)

        # Jumping Jack Button
        jumpingjack_label = wx.StaticText(self.frame, -1, label="Jumping Jack", pos=(420,65), style= wx.ALIGN_RIGHT)
        jumpingjack_label.SetForegroundColour((89,89,89))
        jumpingjack_label.SetFont(label_font)

        jumpingjack_icon = wx.Image("icon/jumpingjack.jpg", wx.BITMAP_TYPE_ANY)
        jumpingjack_icon = jumpingjack_icon.Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        jumpingjack_Btn = wx.BitmapButton(self.frame, -1, jumpingjack_icon, pos=(420,90))
        jumpingjack_Btn.Bind(wx.EVT_BUTTON, self.jumpingjackOnBtn)

        # Confirm Button
        confirm_icon = wx.Image("icon/confirm.jpg", wx.BITMAP_TYPE_ANY)
        confirm_icon = confirm_icon.Scale(40, 40, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        confirm_Btn = wx.BitmapButton(self.frame, -1, confirm_icon, pos=(245,240))
        confirm_Btn.Bind(wx.EVT_BUTTON, self.confirmOnBtn)

        # Home Button
        home_icon = wx.Image("icon/home.jpg", wx.BITMAP_TYPE_ANY)
        home_icon = home_icon.Scale(40, 40, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        home_Btn = wx.BitmapButton(self.frame, -1, home_icon, pos=(325,240))
        home_Btn.Bind(wx.EVT_BUTTON, self.homeOnBtn)

        self.frame.Show()
    
    def situpOnBtn(self, event):
        self.state = "situp"
        
    def squatOnBtn(self, event):
        self.state = "squat"

    def jumpingjackOnBtn(self, event):
        self.state = "jumpingjack"

    def confirmOnBtn(self, event):
        if(self.state == None):
            wx.MessageBox("Please Choose one category", "Error" ,wx.OK | wx.ICON_INFORMATION)  
        else:
            if self.input_type == "Video":
                with wx.FileDialog(self.frame, "Choose Video File", "", "", "Video files (*.mp4, *.avi)|*.mp4", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                    fileDialog.ShowModal()
                    self.video_path = fileDialog.GetPath()
                if self.video_path != "":

                    outputfile, counts_by_frame = run_video(self.video_path, self.state)
                    self.video_path = outputfile

                    result = VideoResultPage(self.video_path, self.state, counts_by_frame)
                    wx.CallAfter(self.frame.Close)
                    result.MainLoop()
            elif self.input_type == "Webcam":
                result = CamResultPage(self.state)
                wx.CallAfter(self.frame.Close)
                result.MainLoop()

    def homeOnBtn(self, event):        
        home = homePage()
        wx.CallAfter(self.frame.Close)
        home.MainLoop()


class VideoResultPage(wx.App):
    def __init__(self, path, state, counts_by_frame):
        wx.App.__init__(self)
        # limit of video size
        limit_height = 800
        limit_width = 800

        # store the video size after scaling
        video_height = 0
        video_width = 0

        # capture video size
        self.capture = cv2.VideoCapture(path)
        ret, rgb = self.capture.read()
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        video_height, video_width = rgb.shape[:2]

        # get scale ratio
        if(video_height > video_width and video_height > limit_height):
            scale_ratio = limit_height / video_height
            video_height = int(limit_height)
            video_width = int(video_width * scale_ratio)
            
        elif(video_height < video_width and video_width > limit_width):
            scale_ratio = limit_width / video_width
            video_height = int(video_height * scale_ratio)
            video_width = int(limit_width)
            
        self.frame = wx.Frame(None, title="Video Result", size = (video_width+300, video_height+110))
        self.frame.SetBackgroundColour("WHITE")

        # NO IDEA icon
        no_idea_icon = wx.Image("icon/noidea.png", wx.BITMAP_TYPE_ANY)
        no_idea_icon = no_idea_icon.Scale(70, 70, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        no_idea_icon = wx.StaticBitmap(self.frame, -1, no_idea_icon, (0, video_height+10))

        # Action label
        if(state == "jumpingjack"):
            action_label = wx.StaticText(self.frame, -1, label = "Jumping Jack", pos = wx.Point(video_width + 60, 10))
            action_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 

        elif(state == "situp"):
            action_label = wx.StaticText(self.frame, -1, label = "Sit-up", pos = wx.Point(video_width + 100, 10))
            action_font = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 

        elif(state == "squat"): 
            action_label = wx.StaticText(self.frame, -1, label = "Squat", pos = wx.Point(video_width + 100, 10))
            action_font = wx.Font(36, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, 'Arial') 

        action_label.SetFont(action_font)
        action_label.SetForegroundColour((234,152,153))

        # Counter label
        counter_label = wx.StaticText(self.frame, -1, label = "Times: ", pos = wx.Point(video_width + 100, 120), style = wx.ALIGN_LEFT)
        counter_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 
        counter_label.SetFont(counter_font)
        counter_label.SetForegroundColour((118,165,174))
        
        
        

        # Back Button
        back_icon = wx.Image("icon/back.jpg", wx.BITMAP_TYPE_ANY)
        back_icon = back_icon.Scale(60, 60, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        back_Btn = wx.BitmapButton(self.frame, -1, back_icon, pos=(video_width + 80, 240))
        back_Btn.Bind(wx.EVT_BUTTON, self.backOnBtn)

        # Home Button
        home_icon = wx.Image("icon/home.jpg", wx.BITMAP_TYPE_ANY)
        home_icon = home_icon.Scale(60, 60, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        home_Btn = wx.BitmapButton(self.frame, -1, home_icon, pos=(video_width + 180, 240))
        home_Btn.Bind(wx.EVT_BUTTON, self.homeOnBtn)
        
        

        # Video Panel
        cap = ShowVideoCapture(self.frame, self.capture, video_height, video_width, counter_label, counts_by_frame, path)
        self.frame.Show()

    def homeOnBtn(self, event):        
        home = homePage()
        wx.CallAfter(self.frame.Close)
        home.MainLoop()

    def backOnBtn(self, event):
        videoPage = VideoPage("Video")
        wx.CallAfter(self.frame.Close)
        videoPage.MainLoop()      



class ShowVideoCapture(wx.Panel):
    def __init__(self, parent, capture, height, width, counter_label, counts_by_frame, path, fps=24):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        # update counter
        self.counter_label = counter_label
        self.path = path

        # time for each frames
        self.counts_by_frame = counts_by_frame

        # frame number for playing on screen
        self.frame_counter = 0        

        # limit size of screen
        self.width = width
        self.height = height

        # set panel size and position
        self.SetSize(width,height)
        self.SetPosition(wx.Point(50,10))

        # capture rgb frame
        self.capture = capture
        ret, rgb = self.capture.read()

        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (self.width, self.height))

        self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, rgb)
        self.fps = fps
        # timer for refresh frame
        self.timer = wx.Timer(self)
        self.timer.Start(int(1000/self.fps))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)
        
        replay_icon = wx.Image("icon/replay.jpg", wx.BITMAP_TYPE_ANY)
        replay_icon = replay_icon.Scale(60, 60, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        replay_Btn = wx.BitmapButton(self.parent, -1, replay_icon, pos=(self.width + 180, 340))
        replay_Btn.Bind(wx.EVT_BUTTON, self.replay)


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        self.frame_counter += 1
        if self.frame_counter>=len(self.counts_by_frame):
            self.frame_counter=len(self.counts_by_frame)-1
        self.counter_label.SetLabel("Times: " + str(self.counts_by_frame[self.frame_counter]))
        ret, rgb = self.capture.read()
        if ret:
            rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(rgb, (self.width, self.height))
            self.bmp.CopyFromBuffer(rgb)
            self.Refresh()
        else:
            self.timer.Stop()
            
    def replay(self, event):
        self.timer.Start(int(1000/self.fps))
        self.frame_counter = 0
        self.capture = cv2.VideoCapture(self.path)


class CamResultPage(wx.App):
    def __init__(self, state):
        wx.App.__init__(self)

        # limit of video size
        limit_height = 800
        limit_width = 800

        # store the webcam size after scaling
        cam_height = 0
        cam_width = 0

        # capture webcam size
        self.capture = cv2.VideoCapture(0)
        ret, rgb = self.capture.read()
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        cam_height, cam_width = rgb.shape[:2]

        # get scale ratio
        if(cam_height > cam_width and cam_height > limit_height):
            scale_ratio = limit_height / cam_height
            cam_height = int(limit_height)
            cam_width = int(cam_width * scale_ratio)
            
        elif(cam_height < cam_width and cam_width > limit_width):
            scale_ratio = limit_width / cam_width
            cam_height = int(cam_height * scale_ratio)
            cam_width = int(limit_width)

        self.frame = wx.Frame(None, title="Webcam Result", size = (cam_width+300, cam_height+110))
        self.frame.SetBackgroundColour("WHITE")

         # NO IDEA icon
        no_idea_icon = wx.Image("icon/noidea.png", wx.BITMAP_TYPE_ANY)
        no_idea_icon = no_idea_icon.Scale(70, 70, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        no_idea_icon = wx.StaticBitmap(self.frame, -1, no_idea_icon, (0, cam_height+10))

        # Action label
        if(state == "jumpingjack"):
            action_label = wx.StaticText(self.frame, -1, label = "Jumping Jack", pos = wx.Point(cam_width + 60, 10))
            action_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 

        elif(state == "situp"):
            action_label = wx.StaticText(self.frame, -1, label = "Sit-up", pos = wx.Point(cam_width + 100, 10))
            action_font = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 

        elif(state == "squat"): 
            action_label = wx.StaticText(self.frame, -1, label = "Squat", pos = wx.Point(cam_width + 100, 10))
            action_font = wx.Font(36, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False, 'Arial') 

        action_label.SetFont(action_font)
        action_label.SetForegroundColour((234,152,153))

        # Counter label
        counter_label = wx.StaticText(self.frame, -1, label = "Times: ", pos = wx.Point(cam_width + 100, 120), style = wx.ALIGN_LEFT)
        counter_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial') 
        counter_label.SetFont(counter_font)
        counter_label.SetForegroundColour((118,165,174))

        # Back Button
        back_icon = wx.Image("icon/back.jpg", wx.BITMAP_TYPE_ANY)
        back_icon = back_icon.Scale(60, 60, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        back_Btn = wx.BitmapButton(self.frame, -1, back_icon, pos=(cam_width + 80, 240))
        back_Btn.Bind(wx.EVT_BUTTON, self.backOnBtn)

        # Home Button
        home_icon = wx.Image("icon/home.jpg", wx.BITMAP_TYPE_ANY)
        home_icon = home_icon.Scale(60, 60, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        home_Btn = wx.BitmapButton(self.frame, -1, home_icon, pos=(cam_width + 180, 240))
        home_Btn.Bind(wx.EVT_BUTTON, self.homeOnBtn)

        # Video Panel
        cap = ShowCamCapture(self.frame, self.capture, cam_height, cam_width, counter_label, state)

        self.frame.Show()
    def homeOnBtn(self, event):        
        home = homePage()
        wx.CallAfter(self.frame.Close)
        home.MainLoop()

    def backOnBtn(self, event):
        videoPage = VideoPage("Webcam")
        wx.CallAfter(self.frame.Close)
        videoPage.MainLoop()   

class ShowCamCapture(wx.Panel):
    def __init__(self, parent, capture, height, width, counter_label, motion, fps=24):
        wx.Panel.__init__(self, parent)
        
        assert motion in ('jumpingjack','situp','squat')

        # set model parameter
        model = "human-pose-estimation-0001.xml"
        device = "CPU"
        self.base_height = 256
        self.inference_engine = InferenceEngine(model, device,8)

        # set parameter for count action          
        self.motion = motion
        self.up=False
        self.count=0

        # label for update counter 
        self.counter_label = counter_label   

        # limit size of screen
        self.width = width
        self.height = height

        # set panel size and position
        self.SetSize(width,height)
        self.SetPosition(wx.Point(50,10))

        # capture rgb frame
        self.capture = capture
        ret, rgb = self.capture.read()

        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, (self.width, self.height))

        self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, rgb)

        self.timer = wx.Timer(self)
        self.timer.Start(1000/fps+1)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, rgb = self.capture.read()
        self.counter_label.SetLabel("Times: " + str(self.count))

        if ret:
            input_scale = self.base_height / rgb.shape[0]
            scaled_img = cv2.resize(rgb, dsize=None, fx=input_scale, fy=input_scale)
            inference_result = self.inference_engine.infer(scaled_img)
            poses_2d = parse_poses(inference_result, input_scale, 8, -1, True)
            draw_poses(rgb, poses_2d)
            if self.motion=="jumpingjack":
                self.up,self.count = count_jumpup(poses_2d,self.up,self.count)
            elif self.motion=="situp":
                self.up,self.count = count_situp(poses_2d,self.up,self.count)
            elif self.motion=="squat":
                self.up,self.count = count_squat(poses_2d,self.up,self.count)
            rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(rgb)
            self.Refresh()
        else:
            self.timer.Stop()
            
if __name__ == '__main__':
    home = homePage()
    #home = VideoPage("Video")
    home.MainLoop()