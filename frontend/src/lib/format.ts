const dateTimeFmt = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const dateFmt = new Intl.DateTimeFormat("pt-BR", {
  weekday: "long",
  day: "2-digit",
  month: "long",
});

export const formatDateTime = (iso: string) => dateTimeFmt.format(new Date(iso));
export const formatLongDate = (iso: string) => dateFmt.format(new Date(iso));

export const formatTime = (iso: string) =>
  new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

export const formatCurrency = (value: string | number | null) => {
  if (value === null || value === "") return "—";
  return Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
};
