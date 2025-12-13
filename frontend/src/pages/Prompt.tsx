import { Icon } from "@iconify-icon/react";
import { Button } from "@/components";
import { GenTestType } from "@/lib/enums";
import type { TestType } from "@/lib/types";
import { useRef, useState } from "react";
import { onSendButton } from "@lib/callbacks";
import type { JSX } from "react";

function Prompt() {
  const reqRef = useRef<HTMLInputElement>(null);
  const productRef = useRef<HTMLInputElement>(null);
  const sendButtonRef = useRef<HTMLButtonElement>(null);
  const testTypeRef = useRef<HTMLSelectElement>(null);

  const [chat_history, setChatHistory] = useState<JSX.Element[]>([]);

  const addHistory = (element: JSX.Element) => {
    setChatHistory((prev) => {
      return [...prev, element];
    });
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-bg text-fg">
      <div className="flex flex-col w-full gap-10 pb-55 items-start m-auto overflow-y-auto grow">
        <h2 className="text-3xl font-bold m-auto p-20">TestOps Copilot</h2>
        {chat_history}
      </div>

      <div className="fixed bottom-0 left-0 w-full flex justify-center">
        <div className="w-full lg:w-[50%] bg-primary p-4 rounded-t-2xl flex flex-col gap-4 shadow-xl">
          <div className="w-full flex flex-row gap-3 items-center">
            <input
              ref={productRef}
              placeholder="Введите название продукта"
              //value="Cloud.ru Calculator"
              onKeyDown={(e) => {
                if (e.key === "Enter") reqRef.current?.focus();
              }}
              className="flex-1 bg-gray-600/50 text-white p-3 rounded-xl outline-none"
            />

            <div className="flex items-center gap-2">
              <label htmlFor="test_type" className="text-sm font-medium">
                Тип Теста:
              </label>

              <select
                ref={testTypeRef}
                id="test_type"
                name="test_type"
                className="bg-secondary text-white px-3 py-2 rounded-xl"
              >
                {Object.entries(GenTestType).map(([value]) => (
                  <option key={value} value={value as TestType}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="w-full flex flex-row gap-3 items-center">
            <input
              ref={reqRef}
              onKeyDown={(e) => {
                if (e.key == "Enter") sendButtonRef.current?.click();
              }}
              placeholder="Введите требования к тест-кейсу"
              //value="Проверить отображение начальной страницы калькулятора Cloud.ru"
              className="flex-1 bg-gray-600/50 text-white p-3 rounded-xl outline-none"
            />

            <Button
              ref={sendButtonRef}
              onClick={() =>
                onSendButton(
                  reqRef,
                  testTypeRef,
                  productRef,
                  addHistory,
                  chat_history
                )
              }
              className="w-12 h-12 flex items-center justify-center rounded-xl hover:bg-accent/75 active:bg-accent/50 transition-colors"
            >
              <Icon
                icon="mingcute:arrow-up-fill"
                className="text-bg rotate-90"
              />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Prompt;
