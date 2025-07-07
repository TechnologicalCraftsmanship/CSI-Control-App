package com.example.espzera;

import android.content.Context; // Adicionado para acessar recursos de string
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.button.MaterialButton;

import java.util.List;

public class UsuarioAdapter extends RecyclerView.Adapter<UsuarioAdapter.UsuarioViewHolder> {

    private List<Usuario> userList;
    private OnUserActionListener listener;
    private Context context; // Adicionado para acessar recursos de string

    // Interface para callbacks de clique nos botões Alterar/Excluir
    public interface OnUserActionListener {
        void onEditClick(Usuario usuario);
        void onDeleteClick(Usuario usuario);
    }

    public UsuarioAdapter(List<Usuario> userList, OnUserActionListener listener, Context context) {
        this.userList = userList;
        this.listener = listener;
        this.context = context; // Inicializa o contexto
    }

    @NonNull
    @Override
    public UsuarioViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_usuario, parent, false);
        return new UsuarioViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull UsuarioViewHolder holder, int position) {
        Usuario currentUser = userList.get(position);
        holder.idTextView.setText(String.valueOf(currentUser.getId()));
        holder.nameTextView.setText(currentUser.getNome());
        // holder.nicknameTextView.setText(currentUser.getApelido()); // Apelido não é mais exibido diretamente

        // Converte o status numérico para string "Ativo" ou "Inativo"
        String[] statusOptions = context.getResources().getStringArray(R.array.status_options); // Corrected: Use R.array
        String statusText;
        if (currentUser.getStatus() == 0) {
            statusText = statusOptions[0]; // "0 - Inativo"
        } else {
            statusText = statusOptions[1]; // "1 - Ativo"
        }
        // Remove "0 - " ou "1 - " do texto
        statusText = statusText.substring(statusText.indexOf("-") + 1).trim();
        holder.statusTextView.setText(statusText);


        holder.alterButton.setOnClickListener(v -> {
            if (listener != null) {
                listener.onEditClick(currentUser);
            }
        });

        holder.deleteButton.setOnClickListener(v -> {
            if (listener != null) {
                listener.onDeleteClick(currentUser);
            }
        });
    }

    @Override
    public int getItemCount() {
        return userList.size();
    }

    // Método para atualizar a lista de usuários no adaptador
    public void updateUsers(List<Usuario> newUserList) {
        this.userList = newUserList;
        notifyDataSetChanged(); // Notifica o RecyclerView que os dados mudaram
    }

    public static class UsuarioViewHolder extends RecyclerView.ViewHolder {
        TextView idTextView;
        TextView nameTextView;
        TextView nicknameTextView;
        TextView statusTextView;
        MaterialButton alterButton;
        MaterialButton deleteButton;

        public UsuarioViewHolder(@NonNull View itemView) {
            super(itemView);
            idTextView = itemView.findViewById(R.id.text_view_user_id);
            nameTextView = itemView.findViewById(R.id.text_view_user_name);
            nicknameTextView = itemView.findViewById(R.id.text_view_user_nickname);
            statusTextView = itemView.findViewById(R.id.text_view_user_status);
            alterButton = itemView.findViewById(R.id.button_alter);
            deleteButton = itemView.findViewById(R.id.button_delete);
        }
    }
}
