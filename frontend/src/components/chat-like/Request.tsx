import type { TestType } from "@lib/types";
import { useEffect, useRef } from "react";

function Request({
  test_type,
  product_name,
  requirement,
}: {
  test_type: TestType;
  product_name: string;
  requirement: string;
}) {
  const component = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    component.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  return (
    <div
      ref={component}
      className="relative flex flex-col self-end bg-primary/40 backdrop-blur-2xl rounded-2xl max-w-[85vw] mr-[3vw] p-5 transition-all duration-150"
    >
      <div className="flex gap-1">
        <p className="font-bold">Тип Теста:</p>
        <p>{test_type}</p>
      </div>
      <div className="flex gap-1">
        <p className="font-bold">Продукт:</p>
        <p>{product_name}</p>
      </div>
      <span>
        <p className="font-bold">Требование:</p>
        <p>{requirement}</p>
      </span>
    </div>
  );
}

export default Request;
