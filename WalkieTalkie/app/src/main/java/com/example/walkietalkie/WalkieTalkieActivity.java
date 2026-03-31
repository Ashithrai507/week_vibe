package com.example.walkietalkie;

import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.view.MotionEvent;
import android.widget.Button;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class WalkieTalkieActivity extends AppCompatActivity {

    TextView userName;
    Button talkButton;

    String targetIP;
    String targetName;

    int PORT = 50005;

    AudioRecord recorder;
    AudioTrack player;
    int bufferSize;

    boolean isRecording = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_walkie_talkie);

        userName = findViewById(R.id.userName);
        talkButton = findViewById(R.id.talkButton);

        targetIP = getIntent().getStringExtra("targetIP");
        targetName = getIntent().getStringExtra("targetName");

        userName.setText("Connected to: " + targetName);

        setupAudio();
        startReceiver();

        talkButton.setOnTouchListener((v, event) -> {
            if (event.getAction() == MotionEvent.ACTION_DOWN) {
                startRecording();
            } else if (event.getAction() == MotionEvent.ACTION_UP) {
                stopRecording();
            }
            return true;
        });
    }

    private void setupAudio() {
        int sampleRate = 44100;

        bufferSize = AudioRecord.getMinBufferSize(
                sampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
        );

        recorder = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize
        );

        player = new AudioTrack(
                android.media.AudioManager.STREAM_MUSIC,
                sampleRate,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize,
                AudioTrack.MODE_STREAM
        );

        player.play();
    }

    private void startRecording() {
        isRecording = true;
        recorder.startRecording();

        new Thread(() -> {
            try {
                DatagramSocket socket = new DatagramSocket();
                InetAddress address = InetAddress.getByName(targetIP);

                byte[] buffer = new byte[bufferSize];

                while (isRecording) {
                    int read = recorder.read(buffer, 0, buffer.length);

                    if (read > 0) {
                        DatagramPacket packet = new DatagramPacket(
                                buffer,
                                read,
                                address,
                                PORT
                        );

                        socket.send(packet);
                    }
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    private void stopRecording() {
        isRecording = false;
        recorder.stop();
    }

    private void startReceiver() {
        new Thread(() -> {
            try {
                DatagramSocket socket = new DatagramSocket(PORT);
                byte[] buffer = new byte[bufferSize];

                while (true) {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);

                    player.write(packet.getData(), 0, packet.getLength());
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }
}