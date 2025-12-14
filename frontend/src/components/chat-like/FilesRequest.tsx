import { useEffect, useRef } from "react";

function FilesRequest({
  files
}: {
  files: FileList | null
}) {
  const component = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    component.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  return (
    <div
      ref={component}
      className="relative flex flex-col self-end bg-primary rounded-2xl max-w-[85vw] mr-[3vw] p-5 transition-all duration-150"
    >
      <p className="font-bold">Улучшение кода из файлов:</p>
      {files !== null && Array.from(files).map((file, index) => (
        <p key={index} >{file.name}</p>
      ))}
    </div>
  );
}

export default FilesRequest;
