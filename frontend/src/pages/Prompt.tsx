import { Icon } from '@iconify-icon/react';
import { Button } from '@/components';
import { GenTestType } from '@/lib/enums';

function Prompt() {
    return (
        <div className="w-screen h-screen">
            <div className='h-full flex items-center justify-center' id="answers">
                <h2 className='text-2xl font-bold'>TestOps Copilot</h2>
            </div>

            <div className='fixed bottom-0 left-0 w-full h-25 bg-primary rounded-t-2xl flex flex-col p-2 gap-2 items-center justify-around'>
                <div className='w-full flex flex-row gap-2'>
                    <label form='test_type'>Тип Теста:</label>
                    <select title="test_type" id='test_type' name='test_type' className='bg-primary border rounded border-bg'>
                        {Object.entries(GenTestType).map(([value]) => (
                            <option>{value}</option>
                        ))}
                    </select>
                </div>

                <div className='w-full flex flex-row gap-4 items-center justify-center'>
                    <input placeholder='Введите тест-кейс' className='bg-gray-600/50 text-white w-full p-2 rounded-2xl'></input>
                    <Button className='w-10 h-10 hover:bg-accent/75 transition-colors duration-300 active:bg-accent/50'>
                        <Icon icon="mingcute:arrow-up-fill" className='rotate-90 text-bg'/>
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default Prompt;