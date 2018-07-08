import sounddevice as sd

from .oscillator import Oscillator
from .sound import (
    EFFECT_SLIDE,
    EFFECT_VIBRATO,
    EFFECT_FADEOUT,
)

SAMPLE_RATE = 22050
BLOCK_SIZE = 2200
CHANNEL_COUNT = 4


class Channel:
    def __init__(self):
        self._oscillator = Oscillator()

        self._is_playing = False
        self._sound = None

        self._time = 0
        self._one_note_time = 0
        self._total_note_time = 0

        self._tone = None
        self._note = 0
        self._pitch = 0
        self._volume = 0
        self._effect = 0

        self._effect_time = 0
        self._effect_pitch = 0
        self._effect_volume = 0

    def play(self, sound, loop):
        self._is_playing = True
        self._is_loop = loop
        self._sound = sound

        self._time = 0
        self._one_note_time = int(sound.speed * SAMPLE_RATE / 120)
        self._total_note_time = self._one_note_time * len(sound.note)

    def stop(self):
        self._is_playing = False
        self._pitch = 0
        self._oscillator.stop()

    def output(self):
        self._update()
        return self._oscillator.output()

    def _update(self):
        if not self._is_playing:
            return

        sound = self._sound

        # forward note
        if self._time % self._one_note_time == 0:
            index = int(self._time / self._one_note_time)
            self._note = sound.note[index]
            self._volume = sound.volume[index] * 1023

            if self._note >= 0 and self._volume > 0:
                last_pitch = self._pitch
                self._tone = sound.tone[index]
                self._pitch = self._note_to_pitch(self._note)
                self._effect = sound.effect[index]

                self._oscillator.set_tone(self._tone)
                self._oscillator.set_period(SAMPLE_RATE // self._pitch)
                self._oscillator.set_volume(self._volume)

                if self._effect == EFFECT_SLIDE:
                    self._effect_time = self._time
                    self._effect_pitch = last_pitch or self._pitch
                elif self._effect == EFFECT_VIBRATO:
                    self._effect_time = self._time
                    self._effect_pitch = self._note_to_pitch(self._note +
                                                             0.5) - self._pitch
                elif self._effect == EFFECT_FADEOUT:
                    self._effect_time = self._time
                    self._effect_volume = self._volume
            else:
                self._oscillator.stop()

        # play note
        if self._note >= 0:
            if self._effect == EFFECT_SLIDE:
                a = ((self._time - self._effect_time) / self._one_note_time)
                pitch = self._pitch * a + self._effect_pitch * (1 - a)
                self._oscillator.set_period(SAMPLE_RATE // pitch)
            elif self._effect == EFFECT_VIBRATO:
                pitch = self._pitch + self._lfo(
                    self._time) * self._effect_pitch
                self._oscillator.set_period(SAMPLE_RATE // pitch)
            elif self._effect == EFFECT_FADEOUT:
                self._oscillator.set_volume(self._effect_volume * (1 - (
                    (self._time - self._effect_time) / self._one_note_time)))

        self._time += 1

        if self._time >= self._total_note_time:
            if self._is_loop:
                self._time = 0
            else:
                self.stop()

    @staticmethod
    def _note_to_pitch(note):
        return 440 * pow(2, (note - 33) / 12)

    @staticmethod
    def _lfo(time):
        x = (time * 8 / SAMPLE_RATE + 0.25) % 1
        return abs(x * 4 - 2) - 1


class AudioPlayer:
    def __init__(self):
        self._output_stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype='int16',
            callback=self._output_stream_callback)

        self._channel_list = [Channel() for _ in range(CHANNEL_COUNT)]

    @property
    def output_stream(self):
        return self._output_stream

    def play(self, ch, sound, *, loop=False):
        self._channel_list[ch].play(sound, loop)

    def stop(self, ch):
        self._channel_list[ch].stop()

    def _output_stream_callback(self, outdata, frames, time, status):
        for i in range(frames):
            output = 0
            for channel in self._channel_list:
                output += channel.output()
            outdata[i] = output
