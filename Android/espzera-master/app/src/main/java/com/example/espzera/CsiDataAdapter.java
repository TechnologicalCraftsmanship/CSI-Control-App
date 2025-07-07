package com.example.espzera;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;
import java.util.Locale;

public class CsiDataAdapter extends RecyclerView.Adapter<CsiDataAdapter.CsiDataViewHolder> {

    private List<CsiData> dataList;

    public CsiDataAdapter(List<CsiData> dataList) {
        this.dataList = dataList;
    }

    @NonNull
    @Override
    public CsiDataViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_csi_data, parent, false);
        return new CsiDataViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CsiDataViewHolder holder, int position) {
        CsiData currentData = dataList.get(position);
        holder.id.setText(String.valueOf(currentData.getId()));
        holder.timestamp.setText(currentData.getDataHora());
        holder.mac.setText(currentData.getMac());
        holder.rssi.setText(String.valueOf(currentData.getRssi()));
        holder.channel.setText(String.format(Locale.getDefault(), "%d (%d)", currentData.getChannel(), currentData.getSecondary_channel()));
    }

    @Override
    public int getItemCount() {
        return dataList.size();
    }

    public void updateData(List<CsiData> newDataList) {
        this.dataList = newDataList;
        notifyDataSetChanged();
    }

    static class CsiDataViewHolder extends RecyclerView.ViewHolder {
        TextView id, timestamp, mac, rssi, channel;

        public CsiDataViewHolder(@NonNull View itemView) {
            super(itemView);
            id = itemView.findViewById(R.id.text_csi_id);
            timestamp = itemView.findViewById(R.id.text_csi_timestamp);
            mac = itemView.findViewById(R.id.text_csi_mac);
            rssi = itemView.findViewById(R.id.text_csi_rssi);
            channel = itemView.findViewById(R.id.text_csi_channel);
        }
    }
}