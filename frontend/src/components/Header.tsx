import { Plus, Scale } from "lucide-react";

interface HeaderProps {
  onNew: () => void;
}

export default function Header({ onNew }: HeaderProps) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="header-icon-wrap">
          <Scale size={22} />
        </div>
        <div>
          <h1 className="header-title">Assistant Juridique personnel de Manu Junior</h1>
          <p className="header-subtitle">Code du numérique · Code général des impôts ___ République du Bénin</p>
        </div>
      </div>
      <button className="btn-new" onClick={onNew}>
        <Plus size={15} />
        Nouvelle conversation
      </button>
    </header>
  );
}
