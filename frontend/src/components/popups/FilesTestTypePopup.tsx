import { useFloating } from "@floating-ui/react";
import { GenTestType } from "@/lib/enums";

function FilesTestTypePopup ({open, files, setOpen, setTestTypes}: {open: boolean, files:FileList | null, setOpen: CallableFunction, setTestTypes?:any}) {
    const { refs, floatingStyles } = useFloating({
        "open": open
    });

    const onSubmit = () => {

    };

    return (
        <>
            {open && (
                <div ref={refs.setFloating} style={floatingStyles} className="w-screen h-screen bg-black/40 z-10 flex justify-center items-center">
                    <div className="flex flex-col gap-2 bg-primary/30 backdrop-blur-2xl p-2 rounded-2xl shadow-2xl">
                        {files != null && Array.from(files).map((file, index) => (
                            <div className="flex items-center gap-2">
                                <p key={index}> Тип теста для {file.name}:</p>
                                <select
                                title="hey"
                                id="test_type"
                                name={file.name}
                                className="bg-primary/40 text-white px-3 py-2 rounded-xl"
                                >
                                {Object.entries(GenTestType).map(([value]) => (
                                    <option key={value} className="bg-primary" value={value as TestType}>
                                    {value}
                                    </option>
                                ))}
                            </select>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </>
    );
};

export default FilesTestTypePopup;