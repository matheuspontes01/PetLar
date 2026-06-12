import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';

import { IonicModule } from '@ionic/angular';

import { UsuariosPage } from './usuarios.page';
import { UsuariosPageRoutingModule } from './usuarios-routing.module';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    UsuariosPageRoutingModule
  ],
  declarations: [UsuariosPage]
})
export class UsuariosPageModule {}
