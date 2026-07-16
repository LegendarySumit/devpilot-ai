import { useState } from "react";

import Navbar from "../../components/layout/Navbar";
import QuickActions from "../../components/sections/QuickActions";
import WorkspaceInput from "../../components/sections/WorkspaceInput";

function HomePage(): JSX.Element {
  const [workspaceValue, setWorkspaceValue] = useState("");

  return (
    <main>
      <Navbar />
      <WorkspaceInput
        value={workspaceValue}
        onChange={setWorkspaceValue}
        onUseExample={setWorkspaceValue}
      />
      <QuickActions onSelect={setWorkspaceValue} />
    </main>
  );
}

export default HomePage;
