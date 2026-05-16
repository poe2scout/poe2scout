export default function Button({
  onClick,
  children,
}: {
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="my-2.5 items-center rounded-md bg-secondary px-5 py-2.5 text-gray-950"
    >
      {children}
    </button>
  );
}
