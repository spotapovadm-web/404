import { useEffect, useRef } from "react";

function FilesRequest({
  files
}: {
  files: Record<string, Array<File>>
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
      <p className="font-bold">Анализ кода из файлов:</p>
      {files !== null && Object.keys(files).map((test_type, index) => (
        <div key={index} className="flex flex-col">
          <span className="flex gap-1">
            <p>Тип Теста: {test_type}</p>
          </span>
          {Array.from(files[test_type]).map((value, index) => (
            <p key={index}>{value.name}</p>
          ))}
        </div>
      ))}
    </div>
  );
}

export default FilesRequest;
