package com.example.walkietalkie;

import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import androidx.appcompat.app.AppCompatActivity;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InterfaceAddress;
import java.net.NetworkInterface;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;

public class MainActivity extends AppCompatActivity {

    ListView userList;
    ArrayList<String> users;
    ArrayAdapter<String> adapter;

    HashSet<String> uniqueUsers = new HashSet<>();

    int PORT = 50006;
    String myName = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        userList = findViewById(R.id.userList);

        users = new ArrayList<>();
        adapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_list_item_1,
                users
        );

        userList.setAdapter(adapter);

        // 🔥 CLICK LISTENER (CALL USER)
        userList.setOnItemClickListener((parent, view, position, id) -> {
            String selectedUser = users.get(position);

            String ip = selectedUser.substring(
                    selectedUser.indexOf("(") + 1,
                    selectedUser.indexOf(")")
            );

            sendCallRequest(ip);
        });

        String name = getUserName();
        if (name == null) {
            askUserName();
        } else {
            myName = name;
            startApp();
        }
    }

    private void startApp() {
        myName = getUserName();
        startBroadcasting();
        startListening();
    }

    // 🔥 SEND CALL REQUEST
    private void sendCallRequest(String targetIp) {
        new Thread(() -> {
            try {
                DatagramSocket socket = new DatagramSocket();

                String message = "CALL:" + myName;
                byte[] data = message.getBytes();

                InetAddress address = InetAddress.getByName(targetIp);

                DatagramPacket packet = new DatagramPacket(
                        data,
                        data.length,
                        address,
                        PORT
                );

                socket.send(packet);

                Log.d("CALL", "Sent call to " + targetIp);

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    // 🔥 BROADCAST YOUR DEVICE
    private void startBroadcasting() {
        new Thread(() -> {
            try {
                DatagramSocket socket = new DatagramSocket();
                socket.setBroadcast(true);

                InetAddress broadcastAddress = getBroadcastAddress();
                if (broadcastAddress == null) return;

                while (true) {
                    String message = "USER:" + myName;
                    byte[] data = message.getBytes();

                    DatagramPacket packet = new DatagramPacket(
                            data,
                            data.length,
                            broadcastAddress,
                            PORT
                    );

                    socket.send(packet);

                    Log.d("BROADCAST", "Sent: " + message);

                    Thread.sleep(2000);
                }

            } catch (Exception e) {
                Log.e("BROADCAST", "Error: " + e.getMessage());
            }
        }).start();
    }

    // 🔥 LISTEN FOR USERS + CALLS
    private void startListening() {
        new Thread(() -> {
            try {
                DatagramSocket socket = new DatagramSocket(null);
                socket.setReuseAddress(true);
                socket.bind(new java.net.InetSocketAddress(PORT));
                socket.setBroadcast(true);

                byte[] buffer = new byte[1024];

                String myIP = getLocalIpAddress();

                while (true) {
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    socket.receive(packet);

                    String msg = new String(packet.getData(), 0, packet.getLength());
                    String ip = packet.getAddress().getHostAddress();

                    Log.d("RECEIVED", msg + " from " + ip);

                    if (ip.equals(myIP)) continue;

                    // 🔔 CALL REQUEST
                    if (msg.startsWith("CALL:")) {
                        String callerName = msg.substring(5);

                        runOnUiThread(() -> {
                            showIncomingCall(callerName, ip);
                        });
                    }

                    // 👥 USER DISCOVERY
                    if (msg.startsWith("USER:")) {
                        String name = msg.substring(5);
                        String userEntry = name + " (" + ip + ")";

                        if (!uniqueUsers.contains(ip)) {
                            uniqueUsers.add(ip);

                            runOnUiThread(() -> {
                                users.add(userEntry);
                                adapter.notifyDataSetChanged();
                            });
                        }
                    }
                }

            } catch (Exception e) {
                Log.e("LISTENER", "Error: " + e.getMessage());
            }
        }).start();
    }

    // 🔔 INCOMING CALL POPUP
    private void showIncomingCall(String callerName, String callerIP) {

        android.app.AlertDialog.Builder builder =
                new android.app.AlertDialog.Builder(this);

        builder.setTitle("Incoming Call");
        builder.setMessage(callerName + " is calling you");

        builder.setPositiveButton("Accept", (dialog, which) -> {
            android.content.Intent intent =
                    new android.content.Intent(this, WalkieTalkieActivity.class);

            intent.putExtra("targetName", callerName);
            intent.putExtra("targetIP", callerIP);

            startActivity(intent);
        });

        builder.setNegativeButton("Reject", null);

        builder.show();
    }

    // 🌐 BROADCAST ADDRESS
    private InetAddress getBroadcastAddress() {
        try {
            NetworkInterface ni = NetworkInterface.getByName("wlan0");
            if (ni == null) return null;

            for (InterfaceAddress ia : ni.getInterfaceAddresses()) {
                if (ia.getBroadcast() != null) {
                    return ia.getBroadcast();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    // 📡 LOCAL IP
    private String getLocalIpAddress() {
        try {
            NetworkInterface ni = NetworkInterface.getByName("wlan0");
            if (ni == null) return "";

            for (InetAddress addr : Collections.list(ni.getInetAddresses())) {
                if (!addr.isLoopbackAddress() && addr instanceof Inet4Address) {
                    return addr.getHostAddress();
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "";
    }

    // 👤 USERNAME STORAGE
    private String getUserName() {
        android.content.SharedPreferences prefs =
                getSharedPreferences("APP_PREFS", MODE_PRIVATE);
        return prefs.getString("username", null);
    }

    private void saveUserName(String name) {
        android.content.SharedPreferences prefs =
                getSharedPreferences("APP_PREFS", MODE_PRIVATE);
        prefs.edit().putString("username", name).apply();
    }

    private void askUserName() {
        android.app.AlertDialog.Builder builder =
                new android.app.AlertDialog.Builder(this);

        builder.setTitle("Enter your name");

        final android.widget.EditText input = new android.widget.EditText(this);
        builder.setView(input);

        builder.setCancelable(false);

        builder.setPositiveButton("OK", (dialog, which) -> {
            String name = input.getText().toString().trim();

            if (name.isEmpty()) {
                name = "User" + (System.currentTimeMillis() % 1000);
            }

            saveUserName(name);
            myName = name;
            startApp();
        });

        builder.show();
    }
}