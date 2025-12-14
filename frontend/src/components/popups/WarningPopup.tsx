import { useEffect, useRef } from "react";

function WarningPopup({
  opened,
  warnings,
  onClose,
}: {
  opened: boolean;
  warnings: Array<string>;
  onClose: CallableFunction;
}) {
  const popupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return opened === true ? (
    <div
      ref={popupRef}
      className="absolute z-50 bg-black/70 backdrop-blur-2xl flex flex-col gap-2 top-[50%] mt-5 left-0 rounded-2xl p-2"
    >
      {warnings &&
        warnings.map((key, index) => (
          <p key={index} className="bg-yellow-300/30 rounded-2xl">{key}</p>
        ))}
    </div>
  ) : null;
}

export default WarningPopup;
