import { Outlet } from "react-router-dom";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <div className="h-screen w-screen">
      <Outlet />
      <Toaster position="bottom-center" toastOptions={{
        style: {
          background: '#316685',
          color: '#ffffff'
        }
      }} />
    </div>
  );
}

export default App;
