import TopNavBar from './TopNavBar';

interface AppShellProps {
  children: React.ReactNode;
  fullHeight?: boolean;
}

export default function AppShell({ children, fullHeight = false }: AppShellProps) {
  return (
    <div className={`flex flex-col min-h-screen bg-[#10141a] ${fullHeight ? 'h-screen overflow-hidden' : ''}`}>
      <TopNavBar />
      {fullHeight ? (
        <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
      ) : (
        <main className="flex-1">{children}</main>
      )}
    </div>
  );
}
