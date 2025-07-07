package com.example.espzera;

import java.io.Serializable;

public class CsiData implements Serializable {
    private int id;
    private String data_hora;
    private String cenario;
    private String type;
    private String mac; // Ordem corrigida
    private int seq;    // Ordem corrigida
    private int rssi;
    private float rate;
    private int sig_mode;
    private int mcs;
    private int bandwidth;
    private int smoothing;
    private int not_sounding;
    private int aggregation;
    private int stbc;
    private int fec_coding;
    private int sgi;
    private int noise_floor;
    private int ampdu_cnt;
    private int channel;
    private int secondary_channel;
    private long local_timestamp;
    private int ant;
    private int sig_len;
    private int rx_state;
    private int len;
    private int first_word;
    private String data;

    // Construtor completo com a ORDEM DE PARÂMETROS CORRIGIDA
    public CsiData(int id, String data_hora, String cenario, String type, String mac, int seq, int rssi, float rate, int sig_mode, int mcs, int bandwidth, int smoothing, int not_sounding, int aggregation, int stbc, int fec_coding, int sgi, int noise_floor, int ampdu_cnt, int channel, int secondary_channel, long local_timestamp, int ant, int sig_len, int rx_state, int len, int first_word, String data) {
        this.id = id;
        this.data_hora = data_hora;
        this.cenario = cenario;
        this.type = type;
        this.mac = mac; // Ordem corrigida
        this.seq = seq; // Ordem corrigida
        this.rssi = rssi;
        this.rate = rate;
        this.sig_mode = sig_mode;
        this.mcs = mcs;
        this.bandwidth = bandwidth;
        this.smoothing = smoothing;
        this.not_sounding = not_sounding;
        this.aggregation = aggregation;
        this.stbc = stbc;
        this.fec_coding = fec_coding;
        this.sgi = sgi;
        this.noise_floor = noise_floor;
        this.ampdu_cnt = ampdu_cnt;
        this.channel = channel;
        this.secondary_channel = secondary_channel;
        this.local_timestamp = local_timestamp;
        this.ant = ant;
        this.sig_len = sig_len;
        this.rx_state = rx_state;
        this.len = len;
        this.first_word = first_word;
        this.data = data;
    }

    // Getters para todos os campos
    public int getId() { return id; }
    public String getDataHora() { return data_hora; }
    public String getCenario() { return cenario; }
    public String getType() { return type; }
    public String getMac() { return mac; }
    public int getSeq() { return seq; }
    public int getRssi() { return rssi; }
    public float getRate() { return rate; }
    public int getSig_mode() { return sig_mode; }
    public int getMcs() { return mcs; }
    public int getBandwidth() { return bandwidth; }
    public int getSmoothing() { return smoothing; }
    public int getNot_sounding() { return not_sounding; }
    public int getAggregation() { return aggregation; }
    public int getStbc() { return stbc; }
    public int getFec_coding() { return fec_coding; }
    public int getSgi() { return sgi; }
    public int getNoise_floor() { return noise_floor; }
    public int getAmpdu_cnt() { return ampdu_cnt; }
    public int getChannel() { return channel; }
    public int getSecondary_channel() { return secondary_channel; }
    public long getLocal_timestamp() { return local_timestamp; }
    public int getAnt() { return ant; }
    public int getSig_len() { return sig_len; }
    public int getRx_state() { return rx_state; }
    public int getLen() { return len; }
    public int getFirst_word() { return first_word; }
    public String getData() { return data; }
}