import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Edit2, X, Save } from "lucide-react";
import { Header } from "@/components/Layout/Header";
import { VehicleCard } from "@/components/Vehicles/VehicleCard";
import { api } from "@/services/api";
import type { Vehicle } from "@/types";

interface FormData {
  name: string;
  plate: string;
  model: string;
  driver: string;
  imei: string;
}

const EMPTY_FORM: FormData = { name: "", plate: "", model: "", driver: "", imei: "" };

export function FleetPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Vehicle | null>(null);
  const [form, setForm] = useState<FormData>(EMPTY_FORM);

  const { data: vehicles = [], isLoading } = useQuery({
    queryKey: ["vehicles"],
    queryFn: api.getVehicles,
    refetchInterval: 30_000,
  });

  const createMut = useMutation({
    mutationFn: api.createVehicle,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["vehicles"] }); closeForm(); },
  });
  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Vehicle> }) =>
      api.updateVehicle(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["vehicles"] }); closeForm(); },
  });
  const deleteMut = useMutation({
    mutationFn: api.deleteVehicle,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["vehicles"] }),
  });

  const openCreate = () => { setEditing(null); setForm(EMPTY_FORM); setShowForm(true); };
  const openEdit = (v: Vehicle) => {
    setEditing(v);
    setForm({ name: v.name, plate: v.plate, model: v.model ?? "", driver: v.driver ?? "", imei: v.imei ?? "" });
    setShowForm(true);
  };
  const closeForm = () => { setShowForm(false); setEditing(null); };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      name: form.name,
      plate: form.plate,
      model: form.model || undefined,
      driver: form.driver || undefined,
      imei: form.imei || undefined,
    };
    if (editing) {
      updateMut.mutate({ id: editing.id, data: payload });
    } else {
      createMut.mutate(payload);
    }
  };

  return (
    <div className="page">
      <Header title="Gestione Flotta" />
      <div className="page-content">
        <div className="toolbar">
          <button className="btn btn-primary" onClick={openCreate}>
            <Plus size={16} /> Aggiungi veicolo
          </button>
        </div>

        {showForm && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h3>{editing ? "Modifica veicolo" : "Nuovo veicolo"}</h3>
                <button className="icon-btn" onClick={closeForm}><X size={18} /></button>
              </div>
              <form className="vehicle-form" onSubmit={handleSubmit}>
                {(["name", "plate", "model", "driver", "imei"] as (keyof FormData)[]).map((f) => (
                  <label key={f} className="form-label">
                    <span>
                      {{ name: "Nome", plate: "Targa", model: "Modello", driver: "Conducente", imei: "IMEI Teltonika" }[f]}
                    </span>
                    <input
                      className="form-input"
                      value={form[f]}
                      required={f === "name" || f === "plate"}
                      onChange={(e) => setForm((p) => ({ ...p, [f]: e.target.value }))}
                    />
                  </label>
                ))}
                <div className="form-actions">
                  <button type="button" className="btn btn-ghost" onClick={closeForm}>Annulla</button>
                  <button type="submit" className="btn btn-primary">
                    <Save size={15} /> Salva
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="loading">Caricamento...</div>
        ) : vehicles.length === 0 ? (
          <div className="empty-state">Nessun veicolo registrato. Aggiungi il primo veicolo.</div>
        ) : (
          <div className="vehicle-grid">
            {vehicles.map((v) => (
              <div key={v.id} className="vehicle-grid-item">
                <VehicleCard vehicle={v} />
                <div className="vehicle-actions">
                  <button className="icon-btn" onClick={() => openEdit(v)}><Edit2 size={15} /></button>
                  <button
                    className="icon-btn icon-btn--danger"
                    onClick={() => {
                      if (confirm(`Eliminare ${v.name}?`)) deleteMut.mutate(v.id);
                    }}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
