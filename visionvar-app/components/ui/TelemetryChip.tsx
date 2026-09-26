interface TelemetryChipProps {
  label: string;
  value: string;
  valueColor?: string;
}

export default function TelemetryChip({ label, value, valueColor = '#dfe2eb' }: TelemetryChipProps) {
  return (
    <div
      className="p-1.5 rounded"
      style={{ background: '#0a0e14' }}
    >
      <span className="text-label-sm font-label-sm text-[#849585] block uppercase tracking-wider">{label}</span>
      <span className="text-label-lg font-label-lg font-bold" style={{ color: valueColor }}>{value}</span>
    </div>
  );
}
