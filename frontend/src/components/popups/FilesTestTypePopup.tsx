import { useFloating } from "@floating-ui/react";
import { useState, useEffect } from "react";
import { GenTestType } from "@/lib/enums";
import type { TestType } from "@/lib/types";

interface FilesTestTypePopupProps {
  open: boolean;
  files: FileList | null;
  setFiles: CallableFunction;
  setOpen: CallableFunction;
}

function FilesTestTypePopup({
  open,
  files,
  setFiles,
  setOpen,
}: FilesTestTypePopupProps) {
  const { refs, floatingStyles } = useFloating({
    open,
  });

  const [selectedTypes, setSelectedTypes] = useState<Record<string, TestType>>(
    {}
  );

  useEffect(() => {
    if (open && files) {
      const initial: Record<string, TestType> = {};
      Array.from(files).forEach((file) => {
        if (!selectedTypes[file.name]) {
          initial[file.name] = Object.keys(GenTestType)[0] as TestType;
        } else {
          initial[file.name] = selectedTypes[file.name];
        }
      });
      setSelectedTypes(initial);
    }
  }, [open, files]);

  const handleChange = (fileName: string, value: TestType) => {
    const updated = { ...selectedTypes, [fileName]: value };
    setSelectedTypes(updated);
    //setTestTypes(updated);
    
  };

  const onSubmit = () => {
    setOpen(false);
    
    
  };

  if (!open) return null;

  return (
    <div
      ref={refs.setFloating}
      style={floatingStyles}
      className="w-screen h-screen bg-black/40 z-10 flex justify-center items-center"
    >
      <div className="flex flex-col gap-4 bg-primary/60 backdrop-blur-2xl p-5 rounded-2xl shadow-2xl">
        {files &&
          Array.from(files).map((file) => (
            <div key={file.name} className="flex items-center gap-2">
              <p>Тип теста для {file.name}:</p>
              <select
                name={file.name}
                value={selectedTypes[file.name]}
                onChange={(e) =>
                  handleChange(file.name, e.target.value as TestType)
                }
                className="bg-primary/40 text-white px-3 py-2 rounded-xl"
              >
                {Object.entries(GenTestType).map(([value]) => (
                  <option key={value} value={value as TestType}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          ))}

        <button
          onClick={onSubmit}
          className="mt-4 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Сохранить
        </button>
      </div>
    </div>
  );
}

export default FilesTestTypePopup;
