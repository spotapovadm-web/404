import { Button } from "@/components";
import GeometricBG from "@/components/backgrounds/GeometricBG";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="w-screen h-screen flex flex-col gap-2 items-center justify-start bg-linear-to-br from-blue-500 to-yellow-200">
      <GeometricBG />
      <h1 className="font-bold z-20 text-4xl pt-[10vh]">Allure.AI</h1>
      <h2 className="z-20 text-3xl">by 404 Team</h2>

      <Button
        onClick={() => navigate("/prompt")}
        className="mt-[30vh] bg-primary/50 border-0 backdrop-blur-2xl lg:w-75 z-20 lg:h-25"
      >
        <span className="text-fg font-bold text-2xl lg:text-5xl">
          Открыть
        </span>
      </Button>
    </div>
  );
}

export default Home;
