package com.example.espzera;

import android.app.Activity;
import android.content.Intent;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.net.Uri;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.textfield.TextInputEditText;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

public class CollectionActivity extends AppCompatActivity {

    private static final String TAG = "CollectionActivity";

    private TextInputEditText espIpInput, collectionTimeInput, cenarioInput;
    private Button discoverButton, selectDbButton, startButton, stopButton;
    private ProgressBar discoveryProgress;
    private TextView consoleOutput, selectedDbPath;
    private ScrollView consoleScroll;
    private Uri targetDbUri;
    private ActivityResultLauncher<Intent> createFileLauncher;
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private DatagramSocket listenSocket;
    private final AtomicBoolean isCollecting = new AtomicBoolean(false);
    private final AtomicBoolean firstPacketReceived = new AtomicBoolean(false);
    private final List<String> csiDataBuffer = new ArrayList<>();
    private CountDownTimer collectionTimer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_collection);
        setupUI();

        createFileLauncher = registerForActivityResult(
                new ActivityResultContracts.StartActivityForResult(),
                result -> {
                    if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
                        targetDbUri = result.getData().getData();
                        if (targetDbUri != null) {
                            String path = targetDbUri.getPath();
                            // Display a user-friendly path or filename, not the full URI path
                            // For content URIs, getPath() might not be what you want to show
                            // A better approach would be to get the display name from the ContentResolver
                            // For simplicity, we'll keep what you had, but be aware of its limitations.
                            selectedDbPath.setText("Saving to: " + path);
                            startButton.setEnabled(true);
                            logToConsole("Output file selected. Ready to start.");
                        }
                    }
                }
        );
        selectDbButton.setOnClickListener(v -> openFileCreator());
        discoverButton.setOnClickListener(v -> startDiscovery());
        startButton.setOnClickListener(v -> startCollection());
        stopButton.setOnClickListener(v -> stopCollection());
    }

    private void setupUI() {
        espIpInput = findViewById(R.id.esp_ip_input);
        collectionTimeInput = findViewById(R.id.collection_time_input);
        cenarioInput = findViewById(R.id.cenario_input);
        discoverButton = findViewById(R.id.discover_button);
        selectDbButton = findViewById(R.id.select_db_button);
        startButton = findViewById(R.id.start_button);
        stopButton = findViewById(R.id.stop_button);
        discoveryProgress = findViewById(R.id.discovery_progress);
        consoleOutput = findViewById(R.id.console_output);
        selectedDbPath = findViewById(R.id.selected_db_path);
        consoleScroll = findViewById(R.id.console_scroll);
        logToConsole("Welcome! Discover an ESP or select a file to begin.");
    }

    private void openFileCreator() {
        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/vnd.sqlite3"); // Mime type for SQLite database
        intent.putExtra(Intent.EXTRA_TITLE, "csi_data_" + System.currentTimeMillis() + ".db");
        createFileLauncher.launch(intent);
    }

    private void startDiscovery() {
        setDiscoveryState(true);
        logToConsole("Searching for ESP32 for 75 seconds...");
        executor.execute(() -> {
            try (DatagramSocket s = new DatagramSocket(50002)) {
                s.setSoTimeout(75000); // 75-second timeout
                byte[] buffer = new byte[1024];
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                s.receive(packet); // This will block until a packet is received or timeout occurs
                String message = new String(packet.getData(), 0, packet.getLength());
                if (message.startsWith("CSI_IP,")) {
                    String discoveredIp = message.split(",")[1];
                    mainHandler.post(() -> {
                        espIpInput.setText(discoveredIp);
                        logToConsole("ESP32 found at: " + discoveredIp);
                    });
                }
            } catch (SocketTimeoutException e) {
                mainHandler.post(() -> logToConsole("ERROR: No ESP32 found within timeout."));
            } catch (Exception e) {
                mainHandler.post(() -> Log.e(TAG, "Error during discovery", e)); // Log full stack trace
                mainHandler.post(() -> logToConsole("ERROR in discovery: " + e.getMessage()));
            } finally {
                mainHandler.post(() -> setDiscoveryState(false));
            }
        });
    }

    private void startCollection() {
        if (targetDbUri == null) {
            Toast.makeText(this, "Please select an output file first.", Toast.LENGTH_SHORT).show();
            return;
        }
        String espIp = espIpInput.getText().toString().trim();
        String timeStr = collectionTimeInput.getText().toString().trim();
        String cenario = cenarioInput.getText().toString().trim();
        if (espIp.isEmpty() || timeStr.isEmpty() || cenario.isEmpty()) {
            Toast.makeText(this, "Please fill in all fields.", Toast.LENGTH_SHORT).show();
            return;
        }

        int collectionTime = Integer.parseInt(timeStr);

        setCollectionState(true);
        isCollecting.set(true);
        firstPacketReceived.set(false);
        csiDataBuffer.clear();

        logToConsole("---------------------------------");
        logToConsole("Starting collection for " + collectionTime + " seconds...");

        executor.execute(this::udpListenerThread); // Start UDP listener
        executor.execute(() -> sendStartCommand(espIp, timeStr)); // Send start command

        collectionTimer = new CountDownTimer(collectionTime * 1000L, 5000L) { // Tick every 5 seconds
            @Override
            public void onTick(long millisUntilFinished) {
                logToConsole("... " + csiDataBuffer.size() + " packets in buffer ...");
            }
            @Override
            public void onFinish() {
                logToConsole("Collection time finished.");
                stopCollection(); // Automatically stop when timer ends
            }
        }.start();
    }

    private void sendStartCommand(String espIp, String time) {
        try (DatagramSocket commandSocket = new DatagramSocket()) {
            // Keep sending 'start' command until first CSI packet is received
            while (isCollecting.get() && !firstPacketReceived.get()) {
                String startMessage = "start," + time;
                byte[] buffer = startMessage.getBytes("UTF-8");
                InetAddress espAddress = InetAddress.getByName(espIp);
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length, espAddress, 50000);
                commandSocket.send(packet);
                logToConsole("Sent 'start' command to " + espIp);
                Thread.sleep(200); // Small delay before resending
            }
        } catch (Exception e) {
            Log.e(TAG, "Error sending 'start' command", e);
            logToConsole("Error sending 'start': " + e.getMessage());
        }
    }

    private void udpListenerThread() {
        try {
            listenSocket = new DatagramSocket(50001);
            logToConsole("Listening for CSI data on port 50001...");
            byte[] buffer = new byte[2048]; // Buffer for incoming UDP packets
            while (isCollecting.get()) {
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                listenSocket.receive(packet); // Blocks until a packet is received
                String data = new String(packet.getData(), 0, packet.getLength()).trim();

                if (data.startsWith("CSI_DATA")) {
                    if (!firstPacketReceived.getAndSet(true)) {
                        logToConsole("First CSI packet received. Stopping 'start' command transmission.");
                    }
                    // For debugging, you might want to only log the raw data if not too verbose
                    // logToConsole(data); // This can flood the console, enable carefully

                    synchronized (csiDataBuffer) {
                        csiDataBuffer.add(data); // Add raw CSI string to buffer
                    }
                }
            }
        } catch (Exception e) {
            // Only log an error if collection was still active (not stopped intentionally)
            if (isCollecting.get()) {
                Log.e(TAG, "Error in UDP listener thread", e);
                logToConsole("Error in listener thread: " + e.getMessage());
            }
        } finally {
            if (listenSocket != null && !listenSocket.isClosed()) {
                listenSocket.close(); // Ensure socket is closed
            }
            logToConsole("Listener thread finished.");
        }
    }

    private void stopCollection() {
        // Use getAndSet to ensure stop logic runs only once per stop request
        if (!isCollecting.getAndSet(false)) return;

        if (collectionTimer != null) {
            collectionTimer.cancel(); // Stop the countdown timer
        }
        if (listenSocket != null) {
            listenSocket.close(); // Close the socket to unblock listener thread
        }

        // Play a notification sound
        try {
            ToneGenerator toneGen = new ToneGenerator(AudioManager.STREAM_NOTIFICATION, 100);
            toneGen.startTone(ToneGenerator.TONE_PROP_BEEP, 200); // Beep sound for 200ms
            new Handler(Looper.getMainLooper()).postDelayed(toneGen::release, 300); // Release after sound plays
        } catch (Exception e) {
            Log.e(TAG, "Failed to play notification beep", e);
        }

        mainHandler.post(() -> {
            setCollectionState(false); // Update UI buttons
            logToConsole("Collection stopped. Saving data...");
            // Delay saving slightly to allow any last buffered packets to be processed or UI to update
            new Handler(Looper.getMainLooper()).postDelayed(this::saveDataToSelectedFile, 500);
        });
    }

    private void saveDataToSelectedFile() {
        final List<String> dataToSave;
        synchronized (csiDataBuffer) {
            if (csiDataBuffer.isEmpty()) {
                logToConsole("No data to save. Buffer is empty.");
                return;
            }
            dataToSave = new ArrayList<>(csiDataBuffer); // Copy data to avoid ConcurrentModification
            csiDataBuffer.clear(); // Clear main buffer
        }

        logToConsole("Starting save for " + dataToSave.size() + " records...");
        executor.execute(() -> {
            File tempDbFile = new File(getCacheDir(), "temp_csi.db");
            if(tempDbFile.exists()) tempDbFile.delete(); // Clean up old temp file

            long successCount = 0;
            try (android.database.sqlite.SQLiteDatabase tempDb = android.database.sqlite.SQLiteDatabase.openOrCreateDatabase(tempDbFile, null)) {
                DatabaseHelper.createCsiDataTable(tempDb); // Ensure table exists
                tempDb.beginTransaction(); // Start transaction for efficiency
                try {
                    String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                    String cenario = cenarioInput.getText().toString(); // Get scenario from input field

                    // --- START OF CORRECTION (FROM ORIGINAL PROMPT) ---
                    for (String line : dataToSave) {
                        // The limit 25 ensures the first 24 fields are separated
                        // and the 25th field (the data array) remains intact.
                        String[] parts = line.trim().split(",", 25);

                        // The 'parts' array will have 25 elements: CSI_DATA, seq, mac, ..., data array
                        if (parts.length == 25) {
                            // Remove "CSI_DATA" and pass the rest to the Helper
                            String[] csiPayload = Arrays.copyOfRange(parts, 1, parts.length);
                            if (DatabaseHelper.addCsiData(tempDb, timestamp, cenario, csiPayload) != -1) {
                                successCount++;
                            }
                        } else {
                            Log.w(TAG, "Discarding packet due to unexpected format. Parts count: " + parts.length + " Data: " + line); // Log warning
                            logToConsole("Packet discarded, unexpected format. Parts: " + parts.length);
                        }
                    }
                    // --- END OF CORRECTION ---

                    tempDb.setTransactionSuccessful(); // Mark transaction as successful
                } finally {
                    tempDb.endTransaction(); // End transaction (commit or rollback)
                }
            } catch (Exception e) {
                Log.e(TAG, "Error writing to temporary DB", e); // Log full stack trace
                mainHandler.post(() -> logToConsole("Error preparing data for saving."));
                return;
            }

            // Copy the temporary database file to the user-selected URI
            try (InputStream in = new FileInputStream(tempDbFile);
                 OutputStream out = getContentResolver().openOutputStream(targetDbUri)) {
                if (out == null) {
                    throw new Exception("Could not open output stream for target URI.");
                }
                byte[] buf = new byte[4096];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }

                long finalCount = successCount; // Capture for use in inner class
                mainHandler.post(() -> {
                    logToConsole("Success! " + finalCount + " out of " + dataToSave.size() + " valid records saved.");
                    Toast.makeText(this, ".db file saved successfully!", Toast.LENGTH_LONG).show();
                });
            } catch (Exception e) {
                Log.e(TAG, "Error copying DB to final file", e);
                mainHandler.post(() -> logToConsole("Error saving final file: " + e.getMessage()));
            } finally {
                // Ensure temporary file is deleted
                if(tempDbFile.exists()) {
                    tempDbFile.delete();
                }
            }
        });
    }

    private void setCollectionState(boolean collecting) {
        startButton.setEnabled(!collecting && targetDbUri != null); // Enable start if not collecting and file selected
        stopButton.setEnabled(collecting); // Enable stop only if collecting
        setFieldsEnabled(!collecting); // Disable input fields during collection
    }

    private void setDiscoveryState(boolean discovering) {
        discoverButton.setEnabled(!discovering); // Disable discover button while discovering
        discoveryProgress.setVisibility(discovering ? View.VISIBLE : View.GONE); // Show/hide progress bar
        setFieldsEnabled(!discovering); // Disable fields during discovery
    }

    private void setFieldsEnabled(boolean enabled) {
        espIpInput.setEnabled(enabled);
        collectionTimeInput.setEnabled(enabled);
        cenarioInput.setEnabled(enabled);
        selectDbButton.setEnabled(enabled);

        // Adjust start/stop button states based on overall state and file selection
        if(enabled) { // If fields are generally enabled (not discovering/collecting)
            startButton.setEnabled(targetDbUri != null); // Only enable start if a file is selected
        } else {
            startButton.setEnabled(false); // Otherwise, start button is disabled
        }
        // Stop button state is primarily managed by setCollectionState, but ensure consistency
        if(!isCollecting.get()) { // If not actively collecting, stop is disabled
            stopButton.setEnabled(false);
        }
        // If isCollecting.get() is true, setCollectionState will ensure stopButton is enabled.
    }


    private void logToConsole(final String message) {
        mainHandler.post(() -> {
            if(consoleOutput != null) {
                consoleOutput.append("\n> " + message);
                // Scroll to the bottom to show latest messages
                if(consoleScroll != null) {
                    consoleScroll.post(() -> consoleScroll.fullScroll(View.FOCUS_DOWN));
                }
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopCollection(); // Ensure collection is stopped when activity is destroyed
        executor.shutdownNow(); // Attempt to shut down all running threads immediately
    }
}