import { Button } from "@/components";
import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    return (
        <div className="w-screen h-screen flex flex-col gap-2 items-center justify-start">
            <h1 className="font-bold text-4xl pt-[10vh]">TestOps Copilot</h1>
            <h2 className="text-gray-400 text-3xl">by 404 Team</h2>

            <Button
                onClick={() => navigate('/prompt')}
                className="mt-[30vh] lg:w-75 lg:h-25"
            >
                <span className="text-gray-600 font-bold text-2xl lg:text-5xl">
                    Открыть
                </span>
            </Button>
        </div>
    );
}

export default Home;