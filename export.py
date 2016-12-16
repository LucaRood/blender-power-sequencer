import bpy
import os
from enum import Enum


class RenderDimensions(Enum):
    """A list of tuples representing X, Y, resolution percentage, pixel ratio X, Y, FPS and FPS base parameters to use for rendering"""
    hd_full = (1920, 1080, 100, 1, 1, 24, 1)
    hd_ready = (1280, 720, 100, 1, 1, 24, 1)


class RenderEncoding(Enum):
    """Tuples that contain preset values for encoding in Blender"""
    youtube = ('H264', 'MPEG4', 'H264', 18, 9000, 9000, 0, 224 * 8, 2048,
               10080000, 'AAC', 192)
    facebook = ('H264', 'MPEG4', 'H264', 18, 6000, 6000, 0, 224 * 8, 2048,
                10080000, 'AAC', 192)


# TODO: move presets to external files?
# TODO: Add presets for Facebook and Twitter
# Then use a single function to call the right preset script, i.e.
# presets/youtube.py
def set_render_dimensions(preset=None):
    """Sets the render parameters: dimensions, pixel ratio, resolution percentage, and framerate"""

    if preset and preset in RenderDimensions:
        render = bpy.context.scene.render
        p = preset.value

        render.resolution_x = p[0]
        render.resolution_y = p[1]
        render.resolution_percentage = p[2]
        render.pixel_aspect_x = p[3]
        render.pixel_aspect_y = p[4]
        render.fps = p[5]
        render.fps_base = p[6]
        return 'Done'
    else:
        return 'Missing preset, operation cancelled'


def set_render_encoding(preset=None):
    """"Sets the render format and ffmpeg encoding settings"""

    if preset and preset in RenderEncoding:
        p = preset.value

        render = bpy.context.scene.render
        ffmpeg = render.ffmpeg

        render.image_settings.file_format = p[0]

        ffmpeg.format = p[1]
        ffmpeg.codec = p[2]
        ffmpeg.gopsize = p[3]
        ffmpeg.video_bitrate = p[4]
        ffmpeg.maxrate = p[5]
        ffmpeg.minrate = p[6]
        ffmpeg.buffersize = p[7]
        ffmpeg.packetsize = p[8]
        ffmpeg.muxrate = p[9]
        ffmpeg.audio_codec = p[10]
        ffmpeg.audio_bitrate = p[11]
        return True
    else:
        print("The preset you asked for doesn't exist")
        return False


# 1 click render video with correct encoding params for Youtube
# Auto sets the file name
# TODO: Add params for rendering
# TODO: Add drop-down menu to pick presets + button to render. Put in video area of the sequencer.
# TODO: Give ability to render lower res videos using the proxies generated by revolver, if revolver is installed
#       The script would automatically switch to the proxy for rendering? Then other operator/function to switch back to full res proxies
# TODO: Optim, check if the strips are proxies or full res before calling
# Revolver's bpy.ops.sequencer.proxy_editing_tofullres() / Check Velvet
# for optim there
class RenderVideoWeb(bpy.types.Operator):
    bl_idname = "gdquest_vse.render_video_web"
    bl_label = "Render for Youtube"
    bl_description = "Quickly export the video next to your blend file for Youtube in HD"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set_render_dimensions(RenderDimensions.hd_full)
        set_render_encoding(RenderEncoding.youtube)

        # Switch to full res with velvet revolver if not yet at full res
        if 'velvet_revolver' in bpy.context.user_preferences.addons.keys():
            bpy.ops.sequencer.proxy_editing_tofullres()

# Set the export filepath
        if bpy.data.is_saved:
            filename = bpy.path.basename(bpy.data.filepath)
            filename = os.path.splitext(filename)[0]
            filename += '.mp4'
            bpy.context.scene.render.filepath = "//" + filename if filename != "" else "Video.mp4"
            bpy.ops.render.render({'dict': "override"},
                                  'INVOKE_DEFAULT',
                                  animation=True)
            pass
        return {"FINISHED"}
