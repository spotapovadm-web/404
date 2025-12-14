export class RetryError extends Error {
    code: string

    constructor(message: string, code = "RETRY_ERROR") {
        super(message);
        this.name = "RetryError";
        this.code = code;
    }
}