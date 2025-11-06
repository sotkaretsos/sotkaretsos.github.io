// Μικρά βοηθητικά components
const NumberInput = ({ value, onChange, min = 0, step = 0.01, placeholder }) => (
  <input
    type="number"
    className="w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
    value={value}
    min={min}
    step={step}
    onChange={(e) => onChange(parseFloat(e.target.value || 0))}
    placeholder={placeholder}
  />
);

const TextInput = ({ value, onChange, placeholder }) => (
  <input
    type="text"
    className="w-full rounded-xl border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
  />
);

const currency = new Intl.NumberFormat("el-GR", { style: "currency", currency: "EUR" });

export default function FarmerProfitApp() {
  const [expenses, setExpenses] = useState([
    { id: crypto.randomUUID(), name: "Σπόροι/Φυτά", amount: 500 },
    { id: crypto.randomUUID(), name: "Λιπάσματα & Φυτοπροστασία", amount: 800 },
    { id: crypto.randomUUID(), name: "Καύσιμα/Ρεύμα", amount: 350 },
  ]);

  const [revenues, setRevenues] = useState([
    { id: crypto.randomUUID(), product: "Λαχανοκομικά", qty: 1200, unit: "kg", price: 1.2 },
  ]);

  const totals = useMemo(() => {
    const totalExpenses = expenses.reduce((s, e) => s + (Number(e.amount) || 0), 0);
    const totalRevenue = revenues.reduce((s, r) => s + (Number(r.qty) || 0) * (Number(r.price) || 0), 0);
    const profit = totalRevenue - totalExpenses;
    const margin = totalRevenue > 0 ? (profit / totalRevenue) * 100 : 0;
    return { totalExpenses, totalRevenue, profit, margin };
  }, [expenses, revenues]);

  const addExpense = () => setExpenses((list) => [...list, { id: crypto.randomUUID(), name: "", amount: 0 }]);
  const removeExpense = (id) => setExpenses((list) => list.filter((x) => x.id !== id));
  const updateExpense = (id, patch) =>
    setExpenses((list) => list.map((x) => (x.id === id ? { ...x, ...patch } : x)));

  const addRevenue = () => setRevenues((list) => [...list, { id: crypto.randomUUID(), product: "", qty: 0, unit: "kg", price: 0 }]);
  const removeRevenue = (id) => setRevenues((list) => list.filter((x) => x.id !== id));
  const updateRevenue = (id, patch) =>
    setRevenues((list) => list.map((x) => (x.id === id ? { ...x, ...patch } : x)));

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Υπολογισμός Καθαρού Κέρδους Αγρότη</h1>
          <div className="text-sm text-gray-600">EUR (€) | απλή εφαρμογή</div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Περίληψη */}
        <section className="lg:col-span-1">
          <div className="rounded-2xl bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Περίληψη</h2>
            <div className="space-y-3">
              <Row label="Σύνολο Εσόδων" value={currency.format(totals.totalRevenue)} accent="text-emerald-700" />
              <Row label="Σύνολο Εξόδων" value={currency.format(totals.totalExpenses)} accent="text-rose-700" />
              <div className="h-px bg-gray-200 my-2" />
              <Row
                label="Καθαρό Κέρδος"
                value={currency.format(totals.profit)}
                accent={totals.profit >= 0 ? "text-emerald-700" : "text-rose-700"}
              />
              <Row label="Περιθώριο Κέρδους" value={`${totals.margin.toFixed(2)}%`} />
            </div>
            <div className="mt-4 text-xs text-gray-500">
              Καθαρό κέρδος = Έσοδα − Έξοδα. Συμπλήρωσε τα πεδία δεξιά για άμεσο υπολογισμό.
            </div>
          </div>
        </section>

        {/* Έσοδα */}
        <section className="lg:col-span-2">
          <div className="rounded-2xl bg-white p-5 shadow-sm mb-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Έσοδα από Πωλήσεις</h2>
              <button onClick={addRevenue} className="rounded-xl bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700">
                + Προσθήκη γραμμής
              </button>
            </div>

            <div className="grid grid-cols-12 gap-2 text-sm font-medium text-gray-600 mb-2">
              <div className="col-span-4">Προϊόν</div>
              <div className="col-span-2">Ποσότητα</div>
              <div className="col-span-2">Μονάδα</div>
              <div className="col-span-2">Τιμή/Μον.</div>
              <div className="col-span-2 text-right">Σύνολο</div>
            </div>
            <div className="space-y-2">
              {revenues.map((r) => (
                <div key={r.id} className="grid grid-cols-12 gap-2 items-center">
                  <div className="col-span-4">
                    <TextInput value={r.product} onChange={(v) => updateRevenue(r.id, { product: v })} placeholder="π.χ. Ντομάτες" />
                  </div>
                  <div className="col-span-2">
                    <NumberInput value={r.qty} onChange={(v) => updateRevenue(r.id, { qty: v })} step={0.01} placeholder="0" />
                  </div>
                  <div className="col-span-2">
                    <TextInput value={r.unit} onChange={(v) => updateRevenue(r.id, { unit: v })} placeholder="kg/τεμ./κιβ." />
                  </div>
                  <div className="col-span-2">
                    <NumberInput value={r.price} onChange={(v) => updateRevenue(r.id, { price: v })} step={0.01} placeholder="0.00" />
                  </div>
                  <div className="col-span-2 text-right font-medium">
                    {currency.format((Number(r.qty) || 0) * (Number(r.price) || 0))}
                  </div>
                  <div className="col-span-12 flex justify-end">
                    <button
                      onClick={() => removeRevenue(r.id)}
                      className="mt-1 text-xs text-rose-600 hover:text-rose-700"
                    >
                      Διαγραφή
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-end text-sm">
              <span className="mr-2 text-gray-600">Σύνολο Εσόδων:</span>
              <span className="font-semibold">{currency.format(totals.totalRevenue)}</span>
            </div>
          </div>

          {/* Έξοδα */}
          <div className="rounded-2xl bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Έξοδα Παραγωγής</h2>
              <button onClick={addExpense} className="rounded-xl bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700">
                + Προσθήκη γραμμής
              </button>
            </div>

            <div className="grid grid-cols-12 gap-2 text-sm font-medium text-gray-600 mb-2">
              <div className="col-span-8">Κατηγορία</div>
              <div className="col-span-4 text-right">Ποσό</div>
            </div>
            <div className="space-y-2">
              {expenses.map((e) => (
                <div key={e.id} className="grid grid-cols-12 gap-2 items-center">
                  <div className="col-span-8">
                    <TextInput value={e.name} onChange={(v) => updateExpense(e.id, { name: v })} placeholder="π.χ. Εργατικά" />
                  </div>
                  <div className="col-span-4">
                    <NumberInput value={e.amount} onChange={(v) => updateExpense(e.id, { amount: v })} step={0.01} placeholder="0.00" />
                  </div>
                  <div className="col-span-12 flex justify-end">
                    <button
                      onClick={() => removeExpense(e.id)}
                      className="mt-1 text-xs text-rose-600 hover:text-rose-700"
                    >
                      Διαγραφή
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-end text-sm">
              <span className="mr-2 text-gray-600">Σύνολο Εξόδων:</span>
              <span className="font-semibold">{currency.format(totals.totalExpenses)}</span>
            </div>
          </div>
        </section>
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-10">
        <div className="mt-6 rounded-2xl bg-emerald-50 p-4 text-sm text-emerald-900">
          <p className="font-medium mb-1">Χρήσιμες σημειώσεις</p>
          <ul className="list-disc ml-5 space-y-1">
            <li>Μπορείς να προσθέτεις/αφαιρείς γραμμές τόσο στα έσοδα όσο και στα έξοδα.</li>
            <li>Το περιθώριο κέρδους υπολογίζεται ως (Καθαρό Κέρδος / Έσοδα) × 100%.</li>
            <li>Οι τιμές είναι ενδεικτικές σε ευρώ (€). Προσαρμόζονται αυτόματα με κάθε αλλαγή.</li>
          </ul>
        </div>
      </footer>
    </div>
  );
}

function Row({ label, value, accent }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-600">{label}</span>
      <span className={`text-base font-semibold ${accent || ""}`}>{value}</span>
    </div>
  );
}
