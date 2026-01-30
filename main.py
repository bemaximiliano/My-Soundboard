import pygame
import base64
import io
import os
import sys
import tempfile
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from plyer import vibrator

# --- 1. FORCE LOCAL FOLDER ACCESS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from sound_data import AUDIO_STRINGS
except ImportError:
    AUDIO_STRINGS = {}

class RobloxSoundboard(App):
    def build(self):
        # --- 2. ANDROID AUDIO COMPATIBILITY SETTINGS ---
        # Frequency: 22050 (easier for mobile chips), Buffer: 4096 (prevents silence/lag)
        pygame.mixer.pre_init(22050, -16, 2, 4096)
        pygame.init()

        # Main Layout
        self.main_layout = BoxLayout(orientation='vertical', spacing=5, padding=10)

        # Header Title
        title_box = BoxLayout(size_hint_y=None, height=100)
        title = Label(
            text="ROBLOX 2007 SOUNDBOARD",
            bold=True, font_size='24sp',
            color=(1, 1, 1, 1)
        )
        title_box.add_widget(title)
        self.main_layout.add_widget(title_box)

        # Search Bar
        self.search_input = TextInput(
            hint_text="Search for a sound (e.g. Ouch)",
            size_hint_y=None, height=110,
            multiline=False,
            padding=[20, 25],
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.search_input.bind(text=self.filter_buttons)
        self.main_layout.add_widget(self.search_input)

        # Scrollable Grid
        self.scroll_root = ScrollView(size_hint=(1, 1))
        self.button_grid = GridLayout(cols=2, spacing=15, padding=[0, 10], size_hint_y=None)
        self.button_grid.bind(minimum_height=self.button_grid.setter('height'))

        # Generate Buttons
        self.create_buttons()

        self.scroll_root.add_widget(self.button_grid)
        self.main_layout.add_widget(self.scroll_root)

        return self.main_layout

    def create_buttons(self, filter_text=""):
        self.button_grid.clear_widgets()
        
        # Sort files so "Collide" and "Ouch" are easy to find
        for filename, b64_data in sorted(AUDIO_STRINGS.items()):
            # Format title: "Rocket_shot.wav" -> "Rocket Shot"
            clean_name = filename.split('.')[0].replace('_', ' ').replace('-', ' ').title()
            
            if filter_text.lower() in clean_name.lower():
                btn = Button(
                    text=clean_name,
                    size_hint_y=None, height=180,
                    background_normal='',
                    background_color=(0.1, 0.45, 0.8, 1), # Roblox Blue
                    font_size='18sp', bold=True
                )
                # Bind playback
                btn.bind(on_press=lambda instance, data=b64_data: self.play_sound(data))
                self.button_grid.add_widget(btn)

    def filter_buttons(self, instance, value):
        self.create_buttons(value)

    def play_sound(self, b64_data):
        try:
            # Haptic Click (if Plyer is installed)
            try: vibrator.vibrate(0.04)
            except: pass
            
            # --- 3. THE TEMP-FILE BYPASS ---
            # Decoding to a physical file bypasses Android memory-access blocks
            audio_bytes = base64.b64decode(b64_data)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            # Load from the fresh temporary path
            sound = pygame.mixer.Sound(temp_path)
            sound.set_volume(1.0)
            
            # Find an open channel and play
            channel = pygame.mixer.find_channel(True)
            if channel:
                channel.play(sound)
            else:
                sound.play()
            
            # Print to console for debugging
            print(f"DEBUG: Playing sound from {temp_path}")

        except Exception as e:
            print(f"PLAYBACK ERROR: {e}")

if __name__ == "__main__":
    RobloxSoundboard().run()
