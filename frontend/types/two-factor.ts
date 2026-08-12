import { LoginResponse } from "./auth"

export interface TwoFactorSetupResponse {
  otpauth_uri: string
  secret: string
}

export interface TwoFactorConfirmRequest {
  code: string
}

export interface TwoFactorConfirmResponse {
  message: string
  backup_codes: string[]
}

export interface TwoFactorVerifyRequest {
  session_token: string
  code: string
}

export interface TwoFactorLoginResponse {
  two_factor_required: true
  session_token: string
}

/**
 * Type guard — narrows the loginUser thunk's union return type.
 * Needed because LoginResponse and TwoFactorLoginResponse share
 * no common discriminant except this field's presence.
 */
export function isTwoFactorResponse(
  payload: LoginResponse | TwoFactorLoginResponse
): payload is TwoFactorLoginResponse {
  return (payload as TwoFactorLoginResponse).two_factor_required === true
}