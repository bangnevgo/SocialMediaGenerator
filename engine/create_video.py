import os
import sys
import subprocess
import argparse
import tempfile

try:
    import config as C
except ImportError:
    from . import config as C

def check_ffmpeg():
    """Verify if FFmpeg is installed and runnable on the system."""
    try:
        # Run a simple version check
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        if result.returncode == 0:
            return True, ""
        return False, f"FFmpeg returned non-zero exit code: {result.returncode}"
    except FileNotFoundError:
        return False, "FFmpeg executable was not found on the system path."
    except Exception as e:
        # Catch dyld or link errors
        err_msg = str(e)
        if "Library not loaded" in err_msg or "dyld" in err_msg:
            return False, "FFmpeg is installed but failing to launch due to a broken library link (dyld error)."
        return False, f"FFmpeg launch failed: {e}"

def suggest_ffmpeg_fix():
    """Output helpful tips on how to restore a broken homebrew ffmpeg installation."""
    print("\n" + "="*60)
    print("WARNING: FFmpeg error detected on your macOS system.")
    print("="*60)
    print("It appears that your Homebrew installation of FFmpeg has broken library links.")
    print("This often happens when homebrew updates dependencies (like x265) but doesn't rebuild FFmpeg.")
    print("\nTo fix this, please open your terminal and run:")
    print("  brew reinstall ffmpeg")
    print("or")
    print("  brew upgrade ffmpeg")
    print("="*60 + "\n")

def compile_video(slides, audio_path, output_path, slide_duration=3):
    """Compile slides and audio into a final vertical video."""
    is_runnable, err = check_ffmpeg()
    
    # Check if ffmpeg failed to boot (e.g. dyld error)
    if not is_runnable:
        print(f"Error checking FFmpeg: {err}")
        suggest_ffmpeg_fix()
        return False
        
    print(f"FFmpeg is available. Commencing compilation of {len(slides)} slides...")
    
    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    temp_dir = tempfile.mkdtemp()
    clip_files = []
    
    try:
        # 1. Generate individual short video clips for each slide image
        for i, slide_path in enumerate(slides):
            if not os.path.exists(slide_path):
                print(f"Error: Slide file not found: {slide_path}")
                return False
                
            temp_clip_path = os.path.join(temp_dir, f"clip_{i}.mp4")
            print(f"Creating video clip {i} from slide: {os.path.basename(slide_path)}")
            
            # Formulate command to convert 1 static image into a 3s vertical MP4 clip
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", slide_path,
                "-c:v", "libx264",
                "-t", str(slide_duration),
                "-pix_fmt", "yuv420p",
                "-vf", C.VIDEO_SCALE_FILTER,
                "-r", str(C.VIDEO_FPS),
                temp_clip_path
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Double check for library load failure inside execution
            if result.returncode != 0:
                if "Library not loaded" in result.stderr or "dyld" in result.stderr:
                    suggest_ffmpeg_fix()
                    return False
                print(f"FFmpeg compilation clip {i} failed with error:")
                print(result.stderr)
                return False
                
            clip_files.append(temp_clip_path)
            
        # 2. Write list of clips to a text file for concatenation
        concat_list_path = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for clip_file in clip_files:
                f.write(f"file '{clip_file}'\n")
                
        # 3. Concatenate clips and add audio if provided
        print("Concatenating clips into final slideshow...")
        
        final_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path]
        
        if audio_path and os.path.exists(audio_path):
            print(f"Adding audio track: {os.path.basename(audio_path)}")
            # Map input 0 (video) and input 1 (audio), set shortest to match video length
            final_cmd += ["-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-shortest"]
        else:
            if audio_path:
                print(f"Warning: Audio file {audio_path} not found. Generating video-only.")
            final_cmd += ["-c:v", "copy"]
            
        final_cmd.append(output_path)
        
        result = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print("Failed to concatenate final video:")
            print(result.stderr)
            return False
            
        print(f"\nFinal video compiled successfully at: {output_path}")
        return True
        
    except Exception as e:
        print(f"An unexpected error occurred during video generation: {e}")
        return False
    finally:
        # Clean up temporary clips
        try:
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Create vertical video slideshows for Reels/TikTok")
    parser.add_argument("--slides", required=True, help="Comma-separated paths to slide images")
    parser.add_argument("--audio", default="", help="Path to background audio file")
    parser.add_argument("--duration", type=int, default=3, help="Duration in seconds for each slide")
    parser.add_argument("--output", required=True, help="Path to write the final vertical MP4 video")
    
    args = parser.parse_args()
    
    slides_list = [s.strip() for s in args.slides.split(",") if s.strip()]
    if not slides_list:
        print("Error: No valid slides provided.")
        sys.exit(1)
        
    success = compile_video(slides_list, args.audio, args.output, args.duration)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
